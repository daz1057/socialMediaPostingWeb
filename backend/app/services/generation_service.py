"""
Generation service for AI text generation with customer info injection.
"""
import logging
import random
import uuid
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.prompt import Prompt
from app.models.customer_info import (
    CustomerInfo,
    CustomerCategory,
    RANDOM_CATEGORIES,
    ALL_PAIRS_CATEGORIES,
    IGNORED_CATEGORIES,
)
from app.models.model_config import ModelConfig
from app.models.credential import Credential
from app.providers import ProviderFactory, GenerationRequest, GenerationResponse
from app.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for orchestrating AI text generation."""

    def __init__(self, db: AsyncSession):
        """Initialize generation service.

        Args:
            db: Database session
        """
        self.db = db

    async def generate_text(
        self,
        user: User,
        prompt_id: int,
        model_config_id: int,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> GenerationResponse:
        """Generate text using AI provider.

        Args:
            user: Current user
            prompt_id: Prompt template ID
            model_config_id: Model configuration ID
            temperature: Temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            GenerationResponse: Generated content or error

        Raises:
            ValueError: If prompt, model config, or credentials not found
        """
        # Generate request ID for logging
        request_id = str(uuid.uuid4())

        try:
            # 1. Load prompt template
            prompt = await self._load_prompt(user.id, prompt_id)
            if not prompt:
                raise ValueError(f"Prompt with ID {prompt_id} not found")

            logger.info(f"[{request_id}] Loaded prompt: {prompt.name}")

            # 2. Load customer info and inject into prompt
            rendered_prompt = await self._inject_customer_info(
                user.id,
                prompt.details,
                prompt.selected_customers,
            )

            logger.info(f"[{request_id}] Customer info injected")

            # 3. Load model configuration
            model_config = await self._load_model_config(user.id, model_config_id)
            if not model_config:
                raise ValueError(f"Model configuration with ID {model_config_id} not found")

            if not model_config.is_enabled:
                raise ValueError(f"Model {model_config.model_id} is disabled")

            logger.info(f"[{request_id}] Using model: {model_config.provider}/{model_config.model_id}")

            # 4. Load and decrypt credentials
            api_key = await self._get_credentials_for_provider(
                user.id,
                model_config.provider,
            )

            # 5. Create provider instance
            provider = ProviderFactory.create_text_provider(
                provider_name=model_config.provider,
                api_key=api_key,
                model_id=model_config.model_id,
            )

            if not provider:
                raise ValueError(f"Provider '{model_config.provider}' not found")

            # 6. Build generation request
            generation_request = GenerationRequest(
                prompt=rendered_prompt,
                system_prompt=None,  # Could add system prompt support later
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # 7. Call provider
            logger.info(f"[{request_id}] Calling AI provider...")
            response = provider.generate(generation_request)

            # Add request ID to response
            response.request_id = request_id

            if response.success:
                logger.info(
                    f"[{request_id}] Generation successful. "
                    f"Tokens: {response.usage.get('total_tokens') if response.usage else 'N/A'}"
                )
            else:
                logger.error(f"[{request_id}] Generation failed: {response.error}")

            return response

        except Exception as e:
            logger.error(f"[{request_id}] Generation service error: {str(e)}", exc_info=True)
            return GenerationResponse(
                content="",
                model_used="",
                provider="",
                error=str(e),
                success=False,
                request_id=request_id,
            )

    async def _load_prompt(self, user_id: int, prompt_id: int) -> Optional[Prompt]:
        """Load prompt template from database.

        Args:
            user_id: User ID
            prompt_id: Prompt ID

        Returns:
            Prompt or None if not found
        """
        result = await self.db.execute(
            select(Prompt).filter(
                Prompt.id == prompt_id,
                Prompt.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def _inject_customer_info(
        self,
        user_id: int,
        prompt_template: str,
        selected_customers: Dict[str, bool],
    ) -> str:
        """Inject customer info into prompt template using desktop app injection rules.

        Rules:
        - RANDOM_CATEGORIES (Pain, Pleasures, Desires, Relatable Truths): Pick ONE random pair
        - ALL_PAIRS_CATEGORIES (Customer Persona, Artist Persona, Brand, In Groups): Include ALL pairs
        - IGNORED_CATEGORIES (Pun Primer, USP, Roles): Skip entirely

        Args:
            user_id: User ID
            prompt_template: Prompt template with placeholders
            selected_customers: Dict of category names that are enabled

        Returns:
            Rendered prompt with customer info injected
        """
        # If no customers selected, return template as-is
        if not selected_customers:
            return prompt_template

        # Get enabled category names
        enabled_categories = [key for key, enabled in selected_customers.items() if enabled]
        if not enabled_categories:
            return prompt_template

        # Map category names to enum values
        category_map = {cat.value: cat for cat in CustomerCategory}
        enabled_enums = []
        for cat_name in enabled_categories:
            if cat_name in category_map:
                cat_enum = category_map[cat_name]
                # Skip ignored categories
                if cat_enum not in IGNORED_CATEGORIES:
                    enabled_enums.append(cat_enum)

        if not enabled_enums:
            return prompt_template

        # Load all selected customer info
        result = await self.db.execute(
            select(CustomerInfo).filter(
                CustomerInfo.user_id == user_id,
                CustomerInfo.category.in_(enabled_enums),
            )
        )
        customer_infos = result.scalars().all()

        # Build context from customer info
        rendered_prompt = prompt_template
        injected_sections = []

        for customer_info in customer_infos:
            category = customer_info.category
            details = customer_info.details or []

            # Skip if no details
            if not details:
                continue

            # Apply injection rules
            if category in RANDOM_CATEGORIES:
                # Pick ONE random pair
                pair = random.choice(details)
                pairs_to_inject = [pair]
            elif category in ALL_PAIRS_CATEGORIES:
                # Include ALL pairs
                pairs_to_inject = details
            else:
                # Should not happen due to earlier filtering, but skip just in case
                continue

            # Format using desktop style
            section = self._format_customer_section(category.value, pairs_to_inject)
            injected_sections.append(section)

        # Append all sections to the prompt
        if injected_sections:
            rendered_prompt += "\n\n" + "\n\n".join(injected_sections)

        return rendered_prompt

    def _format_customer_section(self, category_name: str, pairs: List[Dict]) -> str:
        """Format customer info section in desktop app style.

        Args:
            category_name: Category display name
            pairs: List of {prompt, response} pairs

        Returns:
            Formatted section string
        """
        lines = [f"### Customer {category_name} ###"]

        for pair in pairs:
            prompt_text = pair.get("prompt", "")
            response_text = pair.get("response", "")
            lines.append(f"Prompt: {prompt_text}")
            lines.append(f"Response: {response_text}")

        lines.append(f"### End Customer {category_name} ###")

        return "\n".join(lines)

    async def _load_model_config(
        self,
        user_id: int,
        model_config_id: int,
    ) -> Optional[ModelConfig]:
        """Load model configuration from database.

        Args:
            user_id: User ID
            model_config_id: Model config ID

        Returns:
            ModelConfig or None if not found
        """
        result = await self.db.execute(
            select(ModelConfig).filter(
                ModelConfig.id == model_config_id,
                ModelConfig.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_credentials_for_provider(
        self,
        user_id: int,
        provider: str,
    ) -> str:
        """Get and decrypt credentials for a provider.

        Args:
            user_id: User ID
            provider: Provider name (e.g., 'openai', 'anthropic')

        Returns:
            Decrypted API key

        Raises:
            ValueError: If no credentials found for provider
        """
        # Get valid credential keys for this provider
        valid_keys = ProviderFactory.get_valid_credentials_for_provider(provider, "text")

        if not valid_keys:
            raise ValueError(f"No valid credential keys defined for provider '{provider}'")

        # Try to find credentials matching any of the valid keys
        result = await self.db.execute(
            select(Credential).filter(
                Credential.user_id == user_id,
                Credential.key.in_(valid_keys),
            )
        )
        credential = result.scalars().first()

        if not credential:
            raise ValueError(
                f"No credentials found for provider '{provider}'. "
                f"Please add one of: {', '.join(valid_keys)}"
            )

        # Decrypt and return
        try:
            api_key = decrypt_value(credential.encrypted_value)
            logger.info(f"Decrypted credential '{credential.key}' for provider '{provider}'")
            return api_key
        except Exception as e:
            logger.error(f"Failed to decrypt credential: {str(e)}")
            raise ValueError(f"Failed to decrypt credential: {str(e)}")

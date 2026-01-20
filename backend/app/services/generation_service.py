"""
Generation service for AI text generation with customer info injection.
"""
import logging
import uuid
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.prompt import Prompt
from app.models.customer_info import CustomerInfo
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
        """Inject customer info into prompt template.

        Args:
            user_id: User ID
            prompt_template: Prompt template with placeholders
            selected_customers: Dict of customer info keys that are enabled

        Returns:
            Rendered prompt with customer info injected
        """
        # If no customers selected, return template as-is
        if not selected_customers:
            return prompt_template

        # Load all selected customer info
        enabled_keys = [key for key, enabled in selected_customers.items() if enabled]
        if not enabled_keys:
            return prompt_template

        result = await self.db.execute(
            select(CustomerInfo).filter(
                CustomerInfo.user_id == user_id,
                CustomerInfo.key.in_(enabled_keys),
            )
        )
        customer_infos = result.scalars().all()

        # Build context from customer info
        rendered_prompt = prompt_template

        for customer_info in customer_infos:
            # Convert customer info content to string for injection
            # You can customize this format based on your needs
            content_str = self._format_customer_content(customer_info.key, customer_info.content)

            # Append to prompt (you could also replace placeholders if you have a specific format)
            rendered_prompt += f"\n\n## {customer_info.key}\n{content_str}"

        return rendered_prompt

    def _format_customer_content(self, key: str, content: Dict) -> str:
        """Format customer content for injection into prompt.

        Args:
            key: Customer info key
            content: Customer info content (JSON)

        Returns:
            Formatted string
        """
        # Simple formatting - convert dict to readable string
        lines = []
        for k, v in content.items():
            if isinstance(v, (dict, list)):
                lines.append(f"**{k}**: {v}")
            else:
                lines.append(f"**{k}**: {v}")

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

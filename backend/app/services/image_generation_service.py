"""
Image generation service for AI image generation with provider abstraction.
"""
import logging
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.model_config import ModelConfig
from app.models.credential import Credential
from app.providers import ProviderFactory, ImageGenerationRequest, ImageGenerationResponse
from app.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Service for orchestrating AI image generation."""

    def __init__(self, db: AsyncSession):
        """Initialize image generation service.

        Args:
            db: Database session
        """
        self.db = db

    async def generate_image(
        self,
        user: User,
        prompt: str,
        model_config_id: int,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        n: int = 1,
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: Optional[int] = None,
        guidance: Optional[float] = None,
    ) -> ImageGenerationResponse:
        """Generate image using AI provider.

        Args:
            user: Current user
            prompt: Image description
            model_config_id: Model configuration ID
            size: Image size (DALL-E)
            quality: Image quality (DALL-E 3)
            style: Image style (DALL-E 3)
            n: Number of images
            width: Image width (Flux)
            height: Image height (Flux)
            steps: Inference steps (Flux)
            guidance: Guidance scale (Flux)

        Returns:
            ImageGenerationResponse: Generated image or error
        """
        # Generate request ID for logging
        request_id = str(uuid.uuid4())

        try:
            # 1. Load model configuration
            model_config = await self._load_model_config(user.id, model_config_id)
            if not model_config:
                raise ValueError(f"Model configuration with ID {model_config_id} not found")

            if not model_config.is_enabled:
                raise ValueError(f"Model {model_config.model_id} is disabled")

            logger.info(f"[{request_id}] Using model: {model_config.provider}/{model_config.model_id}")

            # 2. Load and decrypt credentials
            api_key = await self._get_credentials_for_provider(
                user.id,
                model_config.provider,
            )

            # 3. Create provider instance
            provider = ProviderFactory.create_image_provider(
                provider_name=model_config.provider,
                api_key=api_key,
                model_id=model_config.model_id,
            )

            if not provider:
                raise ValueError(f"Image provider '{model_config.provider}' not found")

            # 4. Build generation request with additional params
            additional_params = {
                "size": size,
                "quality": quality,
                "style": style,
                "n": n,
            }

            # Add Flux-specific params if provided
            if width is not None:
                additional_params["width"] = width
            if height is not None:
                additional_params["height"] = height
            if steps is not None:
                additional_params["steps"] = steps
            if guidance is not None:
                additional_params["guidance"] = guidance

            generation_request = ImageGenerationRequest(
                prompt=prompt,
                additional_params=additional_params,
            )

            # 5. Call provider
            logger.info(f"[{request_id}] Calling image provider...")
            response = provider.generate_image(generation_request)

            # Add request ID to response
            response.request_id = request_id

            if response.success:
                logger.info(f"[{request_id}] Image generation successful")
            else:
                logger.error(f"[{request_id}] Image generation failed: {response.error}")

            return response

        except Exception as e:
            logger.error(f"[{request_id}] Image generation service error: {str(e)}", exc_info=True)
            return ImageGenerationResponse(
                model_used="",
                provider="",
                error=str(e),
                success=False,
                request_id=request_id,
            )

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
            provider: Provider name (e.g., 'openai_dalle', 'bfl_flux')

        Returns:
            Decrypted API key

        Raises:
            ValueError: If no credentials found for provider
        """
        # Get valid credential keys for this provider
        valid_keys = ProviderFactory.get_valid_credentials_for_provider(provider, "image")

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

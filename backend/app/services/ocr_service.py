"""
OCR service for processing images and extracting text using vision models.
"""
import base64
import logging
import uuid
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.model_config import ModelConfig
from app.models.credential import Credential
from app.models.template import Template, TemplateCategory
from app.providers import ProviderFactory, VisionRequest, VisionResponse
from app.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)

# Supported image types
SUPPORTED_IMAGE_TYPES = ["png", "jpg", "jpeg", "gif", "webp"]
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

# Default OCR prompt
DEFAULT_OCR_PROMPT = (
    "Extract all text from this image. Return only the extracted text, "
    "preserving the original formatting and structure as much as possible."
)


class OCRService:
    """Service for OCR processing using vision models."""

    def __init__(self, db: AsyncSession):
        """Initialize OCR service.

        Args:
            db: Database session
        """
        self.db = db

    async def process_image(
        self,
        user: User,
        image_data: bytes,
        image_filename: str,
        model_config_id: int,
        custom_prompt: Optional[str] = None,
        template_name: Optional[str] = None,
        template_tags: Optional[List[str]] = None,
    ) -> Tuple[VisionResponse, Optional[Template]]:
        """Process an image and extract text using vision model.

        Args:
            user: Current user
            image_data: Raw image bytes
            image_filename: Original filename (used to determine type)
            model_config_id: Vision model configuration ID
            custom_prompt: Optional custom extraction prompt
            template_name: Optional name for created OCR template
            template_tags: Optional tags for created OCR template

        Returns:
            Tuple of (VisionResponse, Template or None)

        Raises:
            ValueError: If image, model config, or credentials are invalid
        """
        request_id = str(uuid.uuid4())

        try:
            # 1. Validate image
            image_type = self._get_image_type(image_filename)
            if image_type not in SUPPORTED_IMAGE_TYPES:
                raise ValueError(
                    f"Unsupported image type. Supported: {', '.join(SUPPORTED_IMAGE_TYPES)}"
                )

            if len(image_data) > MAX_IMAGE_SIZE_BYTES:
                raise ValueError(
                    f"Image too large. Maximum size: {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB"
                )

            logger.info(f"[{request_id}] Processing image: {image_filename} ({len(image_data)} bytes)")

            # 2. Encode image to base64
            base64_data = base64.b64encode(image_data).decode("utf-8")

            # 3. Load model configuration
            model_config = await self._load_model_config(user.id, model_config_id)
            if not model_config:
                raise ValueError(f"Model configuration with ID {model_config_id} not found")

            if model_config.model_type != "vision":
                raise ValueError(f"Model {model_config.model_id} is not a vision model")

            if not model_config.is_enabled:
                raise ValueError(f"Model {model_config.model_id} is disabled")

            logger.info(f"[{request_id}] Using vision model: {model_config.provider}/{model_config.model_id}")

            # 4. Get credentials (if required by provider)
            api_key = await self._get_credentials_for_provider(
                user.id,
                model_config.provider,
            )

            # 5. Create vision provider
            provider = ProviderFactory.create_vision_provider(
                provider_name=model_config.provider,
                api_key=api_key,
                model_id=model_config.model_id,
            )

            if not provider:
                raise ValueError(f"Vision provider '{model_config.provider}' not found")

            # 6. Build vision request
            vision_request = VisionRequest(
                image_data=base64_data,
                image_type=image_type,
                prompt=custom_prompt or DEFAULT_OCR_PROMPT,
            )

            # 7. Call provider
            logger.info(f"[{request_id}] Calling vision provider...")
            response = provider.extract_text(vision_request)
            response.request_id = request_id

            # 8. Create OCR template if successful
            template = None
            if response.success and response.extracted_text:
                template = await self._create_ocr_template(
                    user_id=user.id,
                    extracted_text=response.extracted_text,
                    template_name=template_name,
                    template_tags=template_tags,
                    image_filename=image_filename,
                )

                if template:
                    logger.info(f"[{request_id}] Created OCR template: {template.id}")

            if response.success:
                logger.info(
                    f"[{request_id}] OCR successful. "
                    f"Extracted {len(response.extracted_text)} characters"
                )
            else:
                logger.error(f"[{request_id}] OCR failed: {response.error}")

            return response, template

        except Exception as e:
            logger.error(f"[{request_id}] OCR service error: {str(e)}", exc_info=True)
            return VisionResponse(
                extracted_text="",
                model_used="",
                provider="",
                error=str(e),
                success=False,
                request_id=request_id,
            ), None

    def _get_image_type(self, filename: str) -> str:
        """Extract image type from filename.

        Args:
            filename: Image filename

        Returns:
            Lowercase image type extension
        """
        if "." not in filename:
            return ""
        ext = filename.rsplit(".", 1)[-1].lower()
        # Normalize jpeg to jpg
        if ext == "jpeg":
            return "jpg"
        return ext

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
        """Get and decrypt credentials for a vision provider.

        For local providers like LM Studio, returns empty string.

        Args:
            user_id: User ID
            provider: Provider name

        Returns:
            Decrypted API key or empty string for local providers
        """
        # Get valid credential keys for this vision provider
        valid_keys = ProviderFactory.get_valid_credentials_for_provider(provider, "vision")

        # Local providers (like LM Studio) don't need credentials
        if not valid_keys:
            logger.info(f"Provider '{provider}' does not require credentials (local)")
            return ""

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

    async def _create_ocr_template(
        self,
        user_id: int,
        extracted_text: str,
        template_name: Optional[str],
        template_tags: Optional[List[str]],
        image_filename: str,
    ) -> Optional[Template]:
        """Create an OCR template from extracted text.

        Args:
            user_id: User ID
            extracted_text: Extracted text content
            template_name: Optional template name
            template_tags: Optional template tags
            image_filename: Original image filename

        Returns:
            Created Template or None if creation fails
        """
        try:
            # Generate name if not provided
            if not template_name:
                # Use filename without extension
                base_name = image_filename.rsplit(".", 1)[0] if "." in image_filename else image_filename
                template_name = f"OCR: {base_name}"

            # Default tags if not provided
            tags = template_tags or ["ocr", "extracted"]

            template = Template(
                name=template_name[:255],  # Ensure name fits
                category=TemplateCategory.OCR,
                tags=tags,
                content=extracted_text,
                user_id=user_id,
            )

            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)

            return template

        except Exception as e:
            logger.error(f"Failed to create OCR template: {str(e)}")
            # Don't fail the whole operation if template creation fails
            return None

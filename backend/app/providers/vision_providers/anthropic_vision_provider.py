# providers/vision_providers/anthropic_vision_provider.py
"""Anthropic Claude Vision provider for OCR/text extraction."""

import logging
from typing import List
from anthropic import Anthropic

from ..base_provider import BaseVisionProvider, VisionRequest, VisionResponse
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class AnthropicVisionProvider(BaseVisionProvider):
    """Anthropic Claude Vision provider for text extraction."""

    PROVIDER_NAME = "anthropic_vision"

    AVAILABLE_MODELS = [
        "claude-opus-4-5-20251101",
        "claude-sonnet-4-5-20250929",
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    VALID_CREDENTIAL_KEYS = ["anthropic_api_key", "claude_api_key"]

    def __init__(self, api_key: str, model_id: str, **kwargs):
        super().__init__(api_key, model_id, **kwargs)
        self.client = Anthropic(api_key=api_key)

    def extract_text(self, request: VisionRequest) -> VisionResponse:
        """Extract text from image using Anthropic's Claude Vision.

        Args:
            request: VisionRequest containing base64 image data

        Returns:
            VisionResponse with extracted text or error
        """
        try:
            # Map image type to media type
            media_type_map = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "gif": "image/gif",
                "webp": "image/webp"
            }
            media_type = media_type_map.get(request.image_type.lower(), "image/png")

            # Build message content with image
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": request.image_data
                    }
                },
                {
                    "type": "text",
                    "text": request.prompt
                }
            ]

            # Build kwargs for API call
            kwargs = {}
            if request.max_tokens:
                kwargs["max_tokens"] = request.max_tokens
            else:
                kwargs["max_tokens"] = 4096  # Default for OCR
            if request.additional_params:
                kwargs.update(request.additional_params)

            logger.info(f"Calling Anthropic Vision API with model {self.model_id}")

            # Make API call
            message = self.client.messages.create(
                model=self.model_id,
                messages=[{"role": "user", "content": content}],
                **kwargs
            )

            # Extract response
            extracted_text = message.content[0].text if message.content else ""
            usage = {
                "prompt_tokens": message.usage.input_tokens,
                "completion_tokens": message.usage.output_tokens,
                "total_tokens": message.usage.input_tokens + message.usage.output_tokens
            } if message.usage else None

            logger.info(f"Anthropic vision extraction successful. Tokens used: {usage.get('total_tokens') if usage else 'N/A'}")

            return VisionResponse(
                extracted_text=extracted_text,
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                usage=usage,
                raw_response={"id": message.id, "model": message.model, "role": message.role},
                success=True
            )

        except Exception as e:
            logger.error(f"Anthropic vision extraction failed: {str(e)}", exc_info=True)
            return VisionResponse(
                extracted_text="",
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                error=str(e),
                success=False
            )

    def validate_credentials(self) -> bool:
        """Validate that credentials are properly configured.

        Returns:
            True if credentials appear valid, False otherwise
        """
        try:
            # Try a minimal API call to validate credentials
            self.client.messages.create(
                model=self.model_id,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info("Anthropic vision credentials validated successfully")
            return True
        except Exception as e:
            logger.error(f"Anthropic vision credential validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_vision_provider("anthropic_vision", AnthropicVisionProvider)

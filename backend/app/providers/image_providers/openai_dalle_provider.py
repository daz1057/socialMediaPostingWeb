"""OpenAI DALL-E image generation provider implementation."""

import logging
from typing import List
from openai import OpenAI

from ..base_provider import BaseImageProvider, ImageGenerationRequest, ImageGenerationResponse
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class OpenAIDalleProvider(BaseImageProvider):
    """OpenAI DALL-E image generation provider."""

    PROVIDER_NAME = "openai_dalle"

    AVAILABLE_MODELS = [
        "dall-e-3",
        "dall-e-2",
    ]

    VALID_CREDENTIAL_KEYS = ["openai_api_key", "chatgpt_api_key"]

    # Size mappings for different models
    DALLE3_SIZES = ["1024x1024", "1792x1024", "1024x1792"]
    DALLE2_SIZES = ["256x256", "512x512", "1024x1024"]

    def __init__(self, api_key: str, model_id: str, **kwargs):
        super().__init__(api_key, model_id, **kwargs)
        self.client = OpenAI(api_key=api_key)

    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using OpenAI's DALL-E API.

        Args:
            request: ImageGenerationRequest with prompt and parameters

        Returns:
            ImageGenerationResponse with base64 image data or error
        """
        try:
            # Extract parameters from additional_params
            params = request.additional_params or {}
            size = params.get("size", "1024x1024")
            quality = params.get("quality", "standard")
            style = params.get("style", "vivid")
            n = params.get("n", 1)

            # Validate size for model
            if self.model_id == "dall-e-3":
                if size not in self.DALLE3_SIZES:
                    size = "1024x1024"
                # DALL-E 3 only supports n=1
                n = 1
            elif self.model_id == "dall-e-2":
                if size not in self.DALLE2_SIZES:
                    size = "1024x1024"

            logger.info(f"Calling DALL-E API with model {self.model_id}, size={size}")

            # Build API call kwargs
            kwargs = {
                "model": self.model_id,
                "prompt": request.prompt,
                "size": size,
                "n": n,
                "response_format": "b64_json",
            }

            # DALL-E 3 specific parameters
            if self.model_id == "dall-e-3":
                kwargs["quality"] = quality
                kwargs["style"] = style

            # Make API call
            response = self.client.images.generate(**kwargs)

            # Extract base64 data
            image_data = response.data[0].b64_json
            revised_prompt = getattr(response.data[0], "revised_prompt", None)

            logger.info(f"DALL-E generation successful")

            return ImageGenerationResponse(
                image_data=image_data,
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                raw_response={
                    "revised_prompt": revised_prompt,
                    "size": size,
                    "quality": quality if self.model_id == "dall-e-3" else None,
                    "style": style if self.model_id == "dall-e-3" else None,
                },
                success=True
            )

        except Exception as e:
            logger.error(f"DALL-E generation failed: {str(e)}", exc_info=True)
            return ImageGenerationResponse(
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
            # Try to list models as a credential validation
            self.client.models.list()
            logger.info("OpenAI DALL-E credentials validated successfully")
            return True
        except Exception as e:
            logger.error(f"OpenAI DALL-E credential validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_image_provider("openai_dalle", OpenAIDalleProvider)

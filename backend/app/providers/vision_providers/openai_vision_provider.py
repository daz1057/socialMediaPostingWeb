# providers/vision_providers/openai_vision_provider.py
"""OpenAI GPT-4 Vision provider for OCR/text extraction."""

import logging
from typing import List
from openai import OpenAI

from ..base_provider import BaseVisionProvider, VisionRequest, VisionResponse
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class OpenAIVisionProvider(BaseVisionProvider):
    """OpenAI GPT-4 Vision provider for text extraction."""

    PROVIDER_NAME = "openai_vision"

    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
    ]

    VALID_CREDENTIAL_KEYS = ["chatgpt_api_key", "openai_api_key"]

    def __init__(self, api_key: str, model_id: str, **kwargs):
        super().__init__(api_key, model_id, **kwargs)
        self.client = OpenAI(api_key=api_key)

    def extract_text(self, request: VisionRequest) -> VisionResponse:
        """Extract text from image using OpenAI's GPT-4 Vision.

        Args:
            request: VisionRequest containing base64 image data

        Returns:
            VisionResponse with extracted text or error
        """
        try:
            # Build image URL (base64 data URL format)
            media_type = f"image/{request.image_type}"
            image_url = f"data:{media_type};base64,{request.image_data}"

            # Build message content
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "high"  # High detail for better OCR
                            }
                        },
                        {
                            "type": "text",
                            "text": request.prompt
                        }
                    ]
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

            logger.info(f"Calling OpenAI Vision API with model {self.model_id}")

            # Make API call
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                **kwargs
            )

            # Extract response
            extracted_text = completion.choices[0].message.content
            usage = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            } if completion.usage else None

            logger.info(f"OpenAI vision extraction successful. Tokens used: {usage.get('total_tokens') if usage else 'N/A'}")

            return VisionResponse(
                extracted_text=extracted_text,
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                usage=usage,
                raw_response={"id": completion.id, "model": completion.model},
                success=True
            )

        except Exception as e:
            logger.error(f"OpenAI vision extraction failed: {str(e)}", exc_info=True)
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
            self.client.models.list()
            logger.info("OpenAI vision credentials validated successfully")
            return True
        except Exception as e:
            logger.error(f"OpenAI vision credential validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_vision_provider("openai_vision", OpenAIVisionProvider)

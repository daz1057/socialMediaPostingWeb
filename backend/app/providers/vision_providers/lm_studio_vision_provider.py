# providers/vision_providers/lm_studio_vision_provider.py
"""LM Studio vision provider for local OCR/text extraction."""

import logging
import httpx
from typing import List

from ..base_provider import BaseVisionProvider, VisionRequest, VisionResponse
from ..provider_factory import ProviderFactory
from ...config import settings

logger = logging.getLogger(__name__)


class LMStudioVisionProvider(BaseVisionProvider):
    """LM Studio vision provider using local LLava models."""

    PROVIDER_NAME = "lm_studio_vision"

    AVAILABLE_MODELS = [
        "llava-1.5-7b",
        "llava-1.6-mistral-7b",
        "llava-1.6-vicuna-7b",
        "llava-v1.6-mistral-7b-gguf",
    ]

    # No API key required for local LM Studio
    VALID_CREDENTIAL_KEYS: List[str] = []

    def __init__(self, api_key: str, model_id: str, **kwargs):
        # api_key is ignored for LM Studio (local)
        super().__init__(api_key, model_id, **kwargs)
        self.base_url = settings.LM_STUDIO_URL.rstrip('/chat/completions')

    def extract_text(self, request: VisionRequest) -> VisionResponse:
        """Extract text from image using LM Studio's vision model.

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
                            "image_url": {"url": image_url}
                        },
                        {
                            "type": "text",
                            "text": request.prompt
                        }
                    ]
                }
            ]

            # Build request payload
            payload = {
                "model": self.model_id,
                "messages": messages,
            }

            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens
            if request.additional_params:
                payload.update(request.additional_params)

            logger.info(f"Calling LM Studio vision API with model {self.model_id}")

            # Make API call to local LM Studio
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

            # Extract response
            extracted_text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            logger.info(f"LM Studio vision extraction successful")

            return VisionResponse(
                extracted_text=extracted_text,
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                } if usage else None,
                raw_response=data,
                success=True
            )

        except httpx.ConnectError as e:
            error_msg = "LM Studio is not running or not accessible. Please start LM Studio and load a vision model."
            logger.error(f"LM Studio connection failed: {str(e)}")
            return VisionResponse(
                extracted_text="",
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                error=error_msg,
                success=False
            )
        except Exception as e:
            logger.error(f"LM Studio vision extraction failed: {str(e)}", exc_info=True)
            return VisionResponse(
                extracted_text="",
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                error=str(e),
                success=False
            )

    def validate_credentials(self) -> bool:
        """Validate that LM Studio is accessible.

        Returns:
            True if LM Studio is running and accessible, False otherwise
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/models")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"LM Studio validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_vision_provider("lm_studio_vision", LMStudioVisionProvider)

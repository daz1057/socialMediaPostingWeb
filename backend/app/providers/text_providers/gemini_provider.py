# providers/text_providers/gemini_provider.py
"""Google Gemini text generation provider implementation."""

import logging
from typing import List
import google.generativeai as genai

from ..base_provider import BaseTextProvider, GenerationRequest, GenerationResponse
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class GeminiProvider(BaseTextProvider):
    """Google Gemini text generation provider."""

    PROVIDER_NAME = "gemini"

    AVAILABLE_MODELS = [
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.0-pro",
    ]

    VALID_CREDENTIAL_KEYS = ["gemini_api_key", "google_ai_api_key"]

    def __init__(self, api_key: str, model_id: str, **kwargs):
        super().__init__(api_key, model_id, **kwargs)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_id)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using Google's Gemini API.

        Args:
            request: GenerationRequest with prompt and parameters

        Returns:
            GenerationResponse with generated content or error
        """
        try:
            # Build generation config
            generation_config = {}
            if request.max_tokens:
                generation_config["max_output_tokens"] = request.max_tokens
            if request.temperature is not None:
                generation_config["temperature"] = request.temperature
            if request.additional_params:
                generation_config.update(request.additional_params)

            # Combine system prompt and user prompt
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"

            logger.info(f"Calling Gemini API with model {self.model_id}")

            # Make API call
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config if generation_config else None
            )

            # Extract response
            content = response.text if response.text else ""

            # Gemini usage metadata (if available)
            usage = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }

            logger.info(f"Gemini generation successful. Tokens used: {usage.get('total_tokens') if usage else 'N/A'}")

            return GenerationResponse(
                content=content,
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                usage=usage,
                raw_response={"model": self.model_id},
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}", exc_info=True)
            return GenerationResponse(
                content="",
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
            response = self.model.generate_content("test")
            logger.info("Gemini credentials validated successfully")
            return True
        except Exception as e:
            logger.error(f"Gemini credential validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_text_provider("gemini", GeminiProvider)

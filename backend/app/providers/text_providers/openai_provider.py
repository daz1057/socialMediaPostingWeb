# providers/text_providers/openai_provider.py
"""OpenAI text generation provider implementation."""

import logging
from typing import List
from openai import OpenAI

from ..base_provider import BaseTextProvider, GenerationRequest, GenerationResponse
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseTextProvider):
    """OpenAI GPT text generation provider."""

    PROVIDER_NAME = "openai"

    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    VALID_CREDENTIAL_KEYS = ["chatgpt_api_key", "openai_api_key"]

    def __init__(self, api_key: str, model_id: str, **kwargs):
        super().__init__(api_key, model_id, **kwargs)
        self.client = OpenAI(api_key=api_key)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using OpenAI's chat completions API.

        Args:
            request: GenerationRequest with prompt and parameters

        Returns:
            GenerationResponse with generated content or error
        """
        try:
            # Build messages for API call
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})

            # Build kwargs for API call
            kwargs = {}
            if request.max_tokens:
                kwargs["max_tokens"] = request.max_tokens
            if request.temperature is not None:
                kwargs["temperature"] = request.temperature
            if request.additional_params:
                kwargs.update(request.additional_params)

            logger.info(f"Calling OpenAI API with model {self.model_id}")

            # Make API call
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                **kwargs
            )

            # Extract response
            content = completion.choices[0].message.content
            usage = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            } if completion.usage else None

            logger.info(f"OpenAI generation successful. Tokens used: {usage.get('total_tokens') if usage else 'N/A'}")

            return GenerationResponse(
                content=content,
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                usage=usage,
                raw_response={"id": completion.id, "model": completion.model},
                success=True
            )

        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}", exc_info=True)
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
            # Try to list models as a credential validation
            self.client.models.list()
            logger.info("OpenAI credentials validated successfully")
            return True
        except Exception as e:
            logger.error(f"OpenAI credential validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_text_provider("openai", OpenAIProvider)

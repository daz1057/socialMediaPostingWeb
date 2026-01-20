# providers/text_providers/anthropic_provider.py
"""Anthropic Claude text generation provider implementation."""

import logging
from typing import List
from anthropic import Anthropic

from ..base_provider import BaseTextProvider, GenerationRequest, GenerationResponse
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseTextProvider):
    """Anthropic Claude text generation provider."""

    PROVIDER_NAME = "anthropic"

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

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using Anthropic's messages API.

        Args:
            request: GenerationRequest with prompt and parameters

        Returns:
            GenerationResponse with generated content or error
        """
        try:
            # Build kwargs for API call
            kwargs = {}
            if request.max_tokens:
                kwargs["max_tokens"] = request.max_tokens
            else:
                kwargs["max_tokens"] = 4096  # Anthropic requires max_tokens

            if request.temperature is not None:
                kwargs["temperature"] = request.temperature
            if request.additional_params:
                kwargs.update(request.additional_params)

            # System prompt handling
            system_prompt = request.system_prompt if request.system_prompt else None

            logger.info(f"Calling Anthropic API with model {self.model_id}")

            # Make API call
            message = self.client.messages.create(
                model=self.model_id,
                messages=[{"role": "user", "content": request.prompt}],
                system=system_prompt,
                **kwargs
            )

            # Extract response
            content = message.content[0].text if message.content else ""
            usage = {
                "prompt_tokens": message.usage.input_tokens,
                "completion_tokens": message.usage.output_tokens,
                "total_tokens": message.usage.input_tokens + message.usage.output_tokens
            } if message.usage else None

            logger.info(f"Anthropic generation successful. Tokens used: {usage.get('total_tokens') if usage else 'N/A'}")

            return GenerationResponse(
                content=content,
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                usage=usage,
                raw_response={"id": message.id, "model": message.model, "role": message.role},
                success=True
            )

        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}", exc_info=True)
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
            self.client.messages.create(
                model=self.model_id,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info("Anthropic credentials validated successfully")
            return True
        except Exception as e:
            logger.error(f"Anthropic credential validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_text_provider("anthropic", AnthropicProvider)

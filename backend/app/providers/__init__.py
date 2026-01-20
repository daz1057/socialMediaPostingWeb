"""AI provider abstraction layer."""

from .base_provider import (
    BaseTextProvider,
    BaseImageProvider,
    GenerationRequest,
    GenerationResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from .provider_factory import ProviderFactory

# Import text providers to trigger registration
from .text_providers import OpenAIProvider, AnthropicProvider, GeminiProvider

# Import image providers to trigger registration
from .image_providers import OpenAIDalleProvider, BFLFluxProvider

__all__ = [
    "BaseTextProvider",
    "BaseImageProvider",
    "GenerationRequest",
    "GenerationResponse",
    "ImageGenerationRequest",
    "ImageGenerationResponse",
    "ProviderFactory",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "OpenAIDalleProvider",
    "BFLFluxProvider",
]

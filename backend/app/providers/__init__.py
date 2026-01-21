"""AI provider abstraction layer."""

from .base_provider import (
    BaseTextProvider,
    BaseImageProvider,
    BaseVisionProvider,
    GenerationRequest,
    GenerationResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
    VisionRequest,
    VisionResponse,
)
from .provider_factory import ProviderFactory

# Import text providers to trigger registration
from .text_providers import OpenAIProvider, AnthropicProvider, GeminiProvider

# Import image providers to trigger registration
from .image_providers import OpenAIDalleProvider, BFLFluxProvider

# Import vision providers to trigger registration
from .vision_providers import LMStudioVisionProvider, OpenAIVisionProvider, AnthropicVisionProvider

__all__ = [
    "BaseTextProvider",
    "BaseImageProvider",
    "BaseVisionProvider",
    "GenerationRequest",
    "GenerationResponse",
    "ImageGenerationRequest",
    "ImageGenerationResponse",
    "VisionRequest",
    "VisionResponse",
    "ProviderFactory",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "OpenAIDalleProvider",
    "BFLFluxProvider",
    "LMStudioVisionProvider",
    "OpenAIVisionProvider",
    "AnthropicVisionProvider",
]

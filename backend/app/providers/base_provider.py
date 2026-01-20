# providers/base_provider.py
"""Abstract base classes and data structures for AI providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class GenerationRequest:
    """Common request structure for text generation providers."""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    additional_params: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResponse:
    """Common response structure from text generation providers."""
    content: str
    model_used: str
    provider: str
    raw_response: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None
    success: bool = True
    request_id: str = ""  # Unique identifier for logging correlation


@dataclass
class ImageGenerationRequest:
    """Common request structure for image generation providers."""
    prompt: str
    aspect_ratio: str = "1:1"
    output_format: str = "png"
    reference_image_path: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None


@dataclass
class ImageGenerationResponse:
    """Common response structure from image generation providers."""
    image_data: Optional[str] = None  # base64 encoded image data
    image_url: Optional[str] = None   # URL to generated image
    model_used: str = ""
    provider: str = ""
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    success: bool = True
    request_id: str = ""  # Unique identifier for logging correlation


class BaseTextProvider(ABC):
    """Abstract base class for text generation providers."""

    PROVIDER_NAME: str = "base"
    AVAILABLE_MODELS: List[str] = []
    VALID_CREDENTIAL_KEYS: List[str] = []

    def __init__(self, api_key: str, model_id: str, **kwargs):
        self.api_key = api_key
        self.model_id = model_id
        self.kwargs = kwargs

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text based on the request.

        Args:
            request: GenerationRequest containing prompt and parameters

        Returns:
            GenerationResponse with generated content or error
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that credentials are properly configured.

        Returns:
            True if credentials appear valid, False otherwise
        """
        pass

    @classmethod
    def get_available_models(cls) -> List[str]:
        """Return list of available model IDs for this provider.

        Returns:
            List of model ID strings
        """
        return cls.AVAILABLE_MODELS

    @classmethod
    def get_valid_credential_keys(cls) -> List[str]:
        """Return list of valid credential keys for this provider.

        Returns:
            List of credential key strings
        """
        return cls.VALID_CREDENTIAL_KEYS


class BaseImageProvider(ABC):
    """Abstract base class for image generation providers."""

    PROVIDER_NAME: str = "base_image"
    AVAILABLE_MODELS: List[str] = []
    VALID_CREDENTIAL_KEYS: List[str] = []

    def __init__(self, api_key: str, model_id: str, **kwargs):
        self.api_key = api_key
        self.model_id = model_id
        self.kwargs = kwargs

    @abstractmethod
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate an image based on the request.

        Args:
            request: ImageGenerationRequest containing prompt and parameters

        Returns:
            ImageGenerationResponse with base64 image data or error
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that credentials are properly configured.

        Returns:
            True if credentials appear valid, False otherwise
        """
        pass

    @classmethod
    def get_available_models(cls) -> List[str]:
        """Return list of available model IDs for this provider.

        Returns:
            List of model ID strings
        """
        return cls.AVAILABLE_MODELS

    @classmethod
    def get_valid_credential_keys(cls) -> List[str]:
        """Return list of valid credential keys for this provider.

        Returns:
            List of credential key strings
        """
        return cls.VALID_CREDENTIAL_KEYS

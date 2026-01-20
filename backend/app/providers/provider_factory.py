# providers/provider_factory.py
"""Factory for creating AI provider instances."""

from typing import Optional, Dict, Type, List
from .base_provider import BaseTextProvider, BaseImageProvider


class ProviderFactory:
    """Factory for creating and managing AI provider instances.

    Uses a registry pattern to allow dynamic registration of new providers.
    """

    _text_providers: Dict[str, Type[BaseTextProvider]] = {}
    _image_providers: Dict[str, Type[BaseImageProvider]] = {}

    @classmethod
    def register_text_provider(cls, name: str, provider_class: Type[BaseTextProvider]) -> None:
        """Register a new text provider.

        Args:
            name: Provider identifier (e.g., 'openai', 'anthropic')
            provider_class: Class implementing BaseTextProvider
        """
        cls._text_providers[name] = provider_class

    @classmethod
    def register_image_provider(cls, name: str, provider_class: Type[BaseImageProvider]) -> None:
        """Register a new image provider.

        Args:
            name: Provider identifier (e.g., 'bfl_flux', 'openai_dalle')
            provider_class: Class implementing BaseImageProvider
        """
        cls._image_providers[name] = provider_class

    @classmethod
    def create_text_provider(
        cls,
        provider_name: str,
        api_key: str,
        model_id: str,
        **kwargs
    ) -> Optional[BaseTextProvider]:
        """Create a text provider instance.

        Args:
            provider_name: Provider identifier
            api_key: API key for authentication
            model_id: Model identifier to use
            **kwargs: Additional provider-specific arguments

        Returns:
            Provider instance or None if provider not found
        """
        provider_class = cls._text_providers.get(provider_name)
        if provider_class:
            return provider_class(api_key=api_key, model_id=model_id, **kwargs)
        return None

    @classmethod
    def create_image_provider(
        cls,
        provider_name: str,
        api_key: str,
        model_id: str,
        **kwargs
    ) -> Optional[BaseImageProvider]:
        """Create an image provider instance.

        Args:
            provider_name: Provider identifier
            api_key: API key for authentication
            model_id: Model identifier to use
            **kwargs: Additional provider-specific arguments

        Returns:
            Provider instance or None if provider not found
        """
        provider_class = cls._image_providers.get(provider_name)
        if provider_class:
            return provider_class(api_key=api_key, model_id=model_id, **kwargs)
        return None

    @classmethod
    def get_available_text_providers(cls) -> List[str]:
        """Return list of registered text provider names.

        Returns:
            List of provider identifier strings
        """
        return list(cls._text_providers.keys())

    @classmethod
    def get_available_image_providers(cls) -> List[str]:
        """Return list of registered image provider names.

        Returns:
            List of provider identifier strings
        """
        return list(cls._image_providers.keys())

    @classmethod
    def get_text_provider_class(cls, provider_name: str) -> Optional[Type[BaseTextProvider]]:
        """Get the class for a text provider.

        Args:
            provider_name: Provider identifier

        Returns:
            Provider class or None if not found
        """
        return cls._text_providers.get(provider_name)

    @classmethod
    def get_image_provider_class(cls, provider_name: str) -> Optional[Type[BaseImageProvider]]:
        """Get the class for an image provider.

        Args:
            provider_name: Provider identifier

        Returns:
            Provider class or None if not found
        """
        return cls._image_providers.get(provider_name)

    @classmethod
    def get_models_for_provider(cls, provider_name: str, provider_type: str = "text") -> List[str]:
        """Get available models for a specific provider.

        Args:
            provider_name: Provider identifier
            provider_type: 'text' or 'image'

        Returns:
            List of model ID strings
        """
        if provider_type == "text":
            provider_class = cls._text_providers.get(provider_name)
        else:
            provider_class = cls._image_providers.get(provider_name)

        if provider_class:
            return provider_class.get_available_models()
        return []

    @classmethod
    def get_valid_credentials_for_provider(cls, provider_name: str, provider_type: str = "text") -> List[str]:
        """Get valid credential keys for a specific provider.

        Args:
            provider_name: Provider identifier
            provider_type: 'text' or 'image'

        Returns:
            List of valid credential key strings
        """
        if provider_type == "text":
            provider_class = cls._text_providers.get(provider_name)
        else:
            provider_class = cls._image_providers.get(provider_name)

        if provider_class:
            return provider_class.get_valid_credential_keys()
        return []

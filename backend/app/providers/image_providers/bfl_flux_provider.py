"""Black Forest Labs Flux image generation provider implementation."""

import logging
import time
import httpx
from typing import List

from ..base_provider import BaseImageProvider, ImageGenerationRequest, ImageGenerationResponse
from ..provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class BFLFluxProvider(BaseImageProvider):
    """Black Forest Labs Flux image generation provider."""

    PROVIDER_NAME = "bfl_flux"

    AVAILABLE_MODELS = [
        "flux-pro-1.1",
        "flux-pro",
        "flux-dev",
    ]

    VALID_CREDENTIAL_KEYS = ["bfl_api_key", "flux_api_key"]

    BASE_URL = "https://api.bfl.ml/v1"

    def __init__(self, api_key: str, model_id: str, **kwargs):
        super().__init__(api_key, model_id, **kwargs)
        self.headers = {
            "X-Key": api_key,
            "Content-Type": "application/json",
        }

    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using BFL Flux API.

        Args:
            request: ImageGenerationRequest with prompt and parameters

        Returns:
            ImageGenerationResponse with base64 image data or error
        """
        try:
            # Extract parameters
            params = request.additional_params or {}
            width = params.get("width", 1024)
            height = params.get("height", 1024)
            steps = params.get("steps", 28)
            guidance = params.get("guidance", 3.5)
            safety_tolerance = params.get("safety_tolerance", 2)

            logger.info(f"Calling BFL Flux API with model {self.model_id}")

            # Build request payload
            payload = {
                "prompt": request.prompt,
                "width": width,
                "height": height,
            }

            # Add model-specific parameters
            if self.model_id in ["flux-pro-1.1", "flux-pro"]:
                payload["steps"] = steps
                payload["guidance"] = guidance
                payload["safety_tolerance"] = safety_tolerance
            elif self.model_id == "flux-dev":
                payload["steps"] = steps
                payload["guidance"] = guidance

            # Determine endpoint based on model
            endpoint = f"{self.BASE_URL}/{self.model_id}"

            # Make async request to start generation
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                # Get the task ID for polling
                task_id = result.get("id")
                if not task_id:
                    raise Exception("No task ID returned from BFL API")

                logger.info(f"BFL task started with ID: {task_id}")

                # Poll for result
                image_data = self._poll_for_result(client, task_id)

                if image_data:
                    logger.info("BFL Flux generation successful")
                    return ImageGenerationResponse(
                        image_data=image_data,
                        model_used=self.model_id,
                        provider=self.PROVIDER_NAME,
                        raw_response={
                            "task_id": task_id,
                            "width": width,
                            "height": height,
                        },
                        success=True
                    )
                else:
                    raise Exception("Failed to retrieve generated image")

        except httpx.HTTPStatusError as e:
            error_msg = f"BFL API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return ImageGenerationResponse(
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                error=error_msg,
                success=False
            )
        except Exception as e:
            logger.error(f"BFL Flux generation failed: {str(e)}", exc_info=True)
            return ImageGenerationResponse(
                model_used=self.model_id,
                provider=self.PROVIDER_NAME,
                error=str(e),
                success=False
            )

    def _poll_for_result(self, client: httpx.Client, task_id: str, max_attempts: int = 60) -> str:
        """Poll BFL API for generation result.

        Args:
            client: httpx client
            task_id: Task ID to poll
            max_attempts: Maximum polling attempts

        Returns:
            Base64 encoded image data or None
        """
        poll_url = f"{self.BASE_URL}/get_result"

        for attempt in range(max_attempts):
            response = client.get(
                poll_url,
                headers=self.headers,
                params={"id": task_id},
            )
            response.raise_for_status()
            result = response.json()

            status = result.get("status")

            if status == "Ready":
                # Get the image URL and download it
                image_url = result.get("result", {}).get("sample")
                if image_url:
                    return self._download_as_base64(client, image_url)
                return None

            elif status == "Error":
                error = result.get("result", {}).get("error", "Unknown error")
                raise Exception(f"BFL generation error: {error}")

            elif status in ["Pending", "Processing"]:
                logger.debug(f"BFL task {task_id} status: {status}, attempt {attempt + 1}")
                time.sleep(1)

            else:
                logger.warning(f"Unknown BFL status: {status}")
                time.sleep(1)

        raise Exception("BFL generation timed out")

    def _download_as_base64(self, client: httpx.Client, url: str) -> str:
        """Download image and convert to base64.

        Args:
            client: httpx client
            url: Image URL

        Returns:
            Base64 encoded image data
        """
        import base64

        response = client.get(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    def validate_credentials(self) -> bool:
        """Validate that credentials are properly configured.

        Returns:
            True if credentials appear valid, False otherwise
        """
        try:
            # Make a simple request to validate credentials
            with httpx.Client(timeout=10.0) as client:
                # Try to get account info or make a minimal request
                response = client.get(
                    f"{self.BASE_URL}/get_result",
                    headers=self.headers,
                    params={"id": "test"},
                )
                # Even a 404 for invalid ID means credentials work
                if response.status_code in [200, 400, 404]:
                    logger.info("BFL Flux credentials validated successfully")
                    return True
                elif response.status_code == 401:
                    logger.error("BFL Flux credential validation failed: unauthorized")
                    return False
            return True
        except Exception as e:
            logger.error(f"BFL Flux credential validation failed: {str(e)}")
            return False


# Auto-register with factory
ProviderFactory.register_image_provider("bfl_flux", BFLFluxProvider)

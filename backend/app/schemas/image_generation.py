"""
Image generation schemas for request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    """Schema for image generation request."""

    prompt: str = Field(..., min_length=1, description="Image description/prompt")
    model_config_id: int = Field(..., description="Model configuration ID to use")
    size: str = Field(default="1024x1024", description="Image size (e.g., 1024x1024, 1792x1024)")
    quality: str = Field(default="standard", description="Image quality (standard/hd) - DALL-E 3 only")
    style: str = Field(default="vivid", description="Image style (vivid/natural) - DALL-E 3 only")
    n: int = Field(default=1, ge=1, le=4, description="Number of images to generate")

    # BFL Flux specific parameters
    width: Optional[int] = Field(default=None, description="Image width in pixels - Flux only")
    height: Optional[int] = Field(default=None, description="Image height in pixels - Flux only")
    steps: Optional[int] = Field(default=None, description="Number of inference steps - Flux only")
    guidance: Optional[float] = Field(default=None, description="Guidance scale - Flux only")


class ImageData(BaseModel):
    """Schema for individual image data."""

    base64_data: str = Field(..., description="Base64 encoded image data")
    format: str = Field(default="png", description="Image format")
    revised_prompt: Optional[str] = Field(None, description="Revised prompt (DALL-E 3)")


class ImageGenerationResponse(BaseModel):
    """Schema for image generation response."""

    images: List[ImageData] = Field(..., description="List of generated images")
    model_used: str = Field(..., description="Model ID used for generation")
    provider: str = Field(..., description="Provider name")
    request_id: str = Field(..., description="Unique request identifier")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw provider response")


class ImageGenerationError(BaseModel):
    """Schema for image generation error response."""

    error: str = Field(..., description="Error message")
    model_used: str = Field(..., description="Model ID attempted")
    provider: str = Field(..., description="Provider name")
    request_id: str = Field(..., description="Unique request identifier")

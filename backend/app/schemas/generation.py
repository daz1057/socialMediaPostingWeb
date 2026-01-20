"""
Generation schemas for AI text/image generation requests and responses.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TextGenerationRequest(BaseModel):
    """Schema for text generation request."""

    prompt_id: int = Field(..., description="Prompt template ID to use")
    model_config_id: int = Field(..., description="Model configuration ID to use")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature (0-2)")
    max_tokens: Optional[int] = Field(None, ge=1, le=100000, description="Maximum tokens to generate")


class TextGenerationResponse(BaseModel):
    """Schema for text generation response."""

    content: str = Field(..., description="Generated text content")
    model_used: str = Field(..., description="Model ID that was used")
    provider: str = Field(..., description="Provider name that was used")
    prompt_id: int = Field(..., description="Prompt template that was used")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")
    success: bool = Field(..., description="Whether generation was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    request_id: str = Field("", description="Unique request ID for logging")

"""
OCR schemas for request/response validation.
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class OCRProcessRequest(BaseModel):
    """Schema for OCR processing request (used internally, not for file upload)."""

    model_config_id: int = Field(..., description="ID of the vision model config to use")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt for text extraction")
    template_name: Optional[str] = Field(None, max_length=255, description="Name for the created OCR template")
    template_tags: Optional[List[str]] = Field(None, description="Tags for the created OCR template")


class OCRProcessResponse(BaseModel):
    """Schema for OCR processing response."""

    extracted_text: str = Field(..., description="Text extracted from the image")
    model_used: str = Field(..., description="Model ID used for extraction")
    provider: str = Field(..., description="Provider name used")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")
    request_id: str = Field(default="", description="Unique request identifier")
    success: bool = Field(default=True, description="Whether extraction was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    template_id: Optional[int] = Field(None, description="ID of created OCR template")
    template_name: Optional[str] = Field(None, description="Name of created OCR template")


class OCRProviderInfo(BaseModel):
    """Schema for OCR/vision provider information."""

    name: str = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Human-readable provider name")
    available_models: List[str] = Field(..., description="List of available model IDs")
    valid_credential_keys: List[str] = Field(..., description="Required credential keys (empty for local)")
    is_local: bool = Field(default=False, description="Whether this is a local provider (no API key needed)")


class OCRProvidersResponse(BaseModel):
    """Schema for listing available OCR providers."""

    providers: List[OCRProviderInfo] = Field(..., description="List of available vision providers")

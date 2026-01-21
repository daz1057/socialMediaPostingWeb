"""
ModelConfig schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ModelConfigBase(BaseModel):
    """Base model config schema."""

    provider: str = Field(..., min_length=1, max_length=50, description="Provider name (e.g., 'openai', 'anthropic')")
    model_id: str = Field(..., min_length=1, max_length=100, description="Model identifier")
    model_type: str = Field(..., pattern="^(text|image|vision)$", description="Model type: 'text', 'image', or 'vision'")


class ModelConfigCreate(ModelConfigBase):
    """Schema for creating a new model config."""

    is_enabled: bool = Field(True, description="Enable this model")
    is_default: bool = Field(False, description="Set as default model for this type")


class ModelConfigUpdate(BaseModel):
    """Schema for updating model config."""

    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None


class ModelConfig(ModelConfigBase):
    """Schema for model config response."""

    id: int
    is_enabled: bool
    is_default: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelConfigList(BaseModel):
    """Schema for paginated model config list response."""

    models: List[ModelConfig]
    total: int
    skip: int
    limit: int


class ProviderInfo(BaseModel):
    """Schema for provider information."""

    name: str
    available_models: List[str]
    valid_credential_keys: List[str]


class ProvidersListResponse(BaseModel):
    """Schema for listing all available providers and their models."""

    text_providers: List[ProviderInfo]
    image_providers: List[ProviderInfo]
    vision_providers: List[ProviderInfo]

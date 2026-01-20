"""
Prompt schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.tag import Tag


class PromptBase(BaseModel):
    """Base prompt schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Prompt name")
    details: str = Field(..., min_length=1, description="Prompt template details")
    selected_customers: Dict[str, bool] = Field(default_factory=dict, description="Customer persona injection flags")
    url: Optional[str] = Field(None, max_length=500, description="OneDrive or reference URL")
    media_file_path: Optional[str] = Field(None, max_length=500, description="Local media file path")
    aws_folder_url: Optional[str] = Field(None, max_length=500, description="AWS S3 folder URL")
    artwork_description: Optional[str] = Field(None, description="Description of artwork/visual")
    example_image: Optional[str] = Field(None, max_length=500, description="Reference image for style guidance")
    tag_id: Optional[int] = Field(None, description="Tag ID (category)")


class PromptCreate(PromptBase):
    """Schema for creating a new prompt."""

    pass


class PromptUpdate(BaseModel):
    """Schema for updating a prompt."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    details: Optional[str] = Field(None, min_length=1)
    selected_customers: Optional[Dict[str, bool]] = None
    url: Optional[str] = Field(None, max_length=500)
    media_file_path: Optional[str] = Field(None, max_length=500)
    aws_folder_url: Optional[str] = Field(None, max_length=500)
    artwork_description: Optional[str] = None
    example_image: Optional[str] = Field(None, max_length=500)
    tag_id: Optional[int] = None


class Prompt(PromptBase):
    """Schema for prompt response."""

    id: int
    user_id: int
    tag: Optional[Tag] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptList(BaseModel):
    """Schema for paginated prompt list response."""

    prompts: List[Prompt]
    total: int
    skip: int
    limit: int

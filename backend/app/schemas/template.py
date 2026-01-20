"""
Template schemas for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TemplateCategory(str, Enum):
    """Template category enumeration for Pydantic."""
    OCR = "ocr"
    MANUAL = "manual"
    CUSTOM = "custom"


class TemplateBase(BaseModel):
    """Base template schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    category: TemplateCategory = Field(default=TemplateCategory.MANUAL, description="Template category")
    tags: List[str] = Field(default_factory=list, description="List of tags for filtering")
    content: str = Field(..., min_length=1, description="Template content")


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""

    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[TemplateCategory] = None
    tags: Optional[List[str]] = None
    content: Optional[str] = Field(None, min_length=1)


class Template(TemplateBase):
    """Schema for template response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateList(BaseModel):
    """Schema for paginated template list response."""

    templates: List[Template]
    total: int
    skip: int
    limit: int

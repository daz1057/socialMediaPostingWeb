"""
Post schemas for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PostStatus(str, Enum):
    """Post status enumeration for Pydantic."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


# Common graphic types
GRAPHIC_TYPES = [
    "Infographic",
    "Short Video",
    "Illustration",
    "Photo",
    "Carousel",
    "Quote",
    "Meme",
    "Story",
    "Reel",
    "Other",
]


class PostBase(BaseModel):
    """Base post schema."""

    content: str = Field(..., min_length=1, description="Post content")
    caption: Optional[str] = Field(None, description="Platform-specific caption")
    alt_text: Optional[str] = Field(None, description="Accessibility text for images")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Post status")
    graphic_type: Optional[str] = Field(None, max_length=100, description="Type of graphic (Infographic, Short Video, etc.)")
    source_url: Optional[str] = Field(None, max_length=500, description="Source URL for reference")
    original_prompt_name: Optional[str] = Field(None, max_length=255, description="Name of source prompt")
    keep: bool = Field(default=False, description="Ready to publish flag")
    for_deletion: bool = Field(default=False, description="Mark for deletion flag")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")
    prompt_id: Optional[int] = Field(None, description="Source prompt ID (if generated from prompt)")


class PostCreate(PostBase):
    """Schema for creating a new post."""

    media_urls: List[str] = Field(default_factory=list, description="Media URLs (S3)")


class PostUpdate(BaseModel):
    """Schema for updating a post."""

    content: Optional[str] = Field(None, min_length=1)
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    status: Optional[PostStatus] = None
    graphic_type: Optional[str] = Field(None, max_length=100)
    source_url: Optional[str] = Field(None, max_length=500)
    original_prompt_name: Optional[str] = Field(None, max_length=255)
    keep: Optional[bool] = None
    for_deletion: Optional[bool] = None
    is_archived: Optional[bool] = None
    scheduled_at: Optional[datetime] = None
    prompt_id: Optional[int] = None
    media_urls: Optional[List[str]] = None


class Post(PostBase):
    """Schema for post response."""

    id: int
    user_id: int
    media_urls: List[str]
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostList(BaseModel):
    """Schema for paginated post list response."""

    posts: List[Post]
    total: int
    skip: int
    limit: int


class MediaUploadResponse(BaseModel):
    """Schema for media upload response."""

    s3_url: str = Field(..., description="S3 URL of uploaded file")
    s3_key: str = Field(..., description="S3 key of uploaded file")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="File content type")


class CSVExportRequest(BaseModel):
    """Schema for CSV export request parameters."""

    status: Optional[PostStatus] = Field(None, description="Filter by status")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")

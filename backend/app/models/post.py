"""
Post model for social media content management.
"""
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class PostStatus(PyEnum):
    """Post status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


class Post(Base, TimestampMixin):
    """Post model for social media content."""

    __tablename__ = "posts"

    # Content
    content = Column(Text, nullable=False)
    caption = Column(Text, nullable=True)  # Platform-specific caption
    alt_text = Column(Text, nullable=True)  # Accessibility text for images
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT, nullable=False, index=True)

    # Post type/classification
    graphic_type = Column(String(100), nullable=True)  # Infographic, Short Video, Illustration, etc.

    # Source tracking
    original_prompt_name = Column(String(255), nullable=True)  # Track source prompt name
    source_url = Column(String(500), nullable=True)  # URL field for source tracking

    # Curation flags
    keep = Column(Boolean, default=False, nullable=False)  # Ready to publish flag
    for_deletion = Column(Boolean, default=False, nullable=False)  # Mark for deletion flag

    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    # Media attachments (S3 URLs stored as JSON array)
    media_urls = Column(JSON, nullable=False, default=list)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="posts")
    prompt = relationship("Prompt", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, status={self.status.value}, user_id={self.user_id})>"

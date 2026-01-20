"""
Prompt model for AI generation templates.
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Prompt(Base, TimestampMixin):
    """Prompt template model with customer persona injection flags."""

    __tablename__ = "prompts"

    name = Column(String(255), nullable=False, index=True)
    details = Column(Text, nullable=False)

    # Customer persona injection flags (stored as JSON)
    selected_customers = Column(JSON, nullable=False, default=dict)

    # Optional metadata
    url = Column(String(500), nullable=True)
    media_file_path = Column(String(500), nullable=True)
    aws_folder_url = Column(String(500), nullable=True)
    artwork_description = Column(Text, nullable=True)
    example_image = Column(String(500), nullable=True)  # Reference image for style guidance

    # Foreign keys
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    tag = relationship("Tag", back_populates="prompts")
    user = relationship("User", back_populates="prompts")
    posts = relationship("Post", back_populates="prompt")

    def __repr__(self):
        return f"<Prompt(id={self.id}, name={self.name}, tag={self.tag.name if self.tag else None})>"

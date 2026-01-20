"""
Tag model for categorizing prompts and posts.
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Tag(Base, TimestampMixin):
    """Tag model for post categories (Entertain, Teach, Learn, Sell, etc.)."""

    __tablename__ = "tags"

    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    prompts = relationship("Prompt", back_populates="tag")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"

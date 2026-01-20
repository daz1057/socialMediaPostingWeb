"""
Template model for reusable text snippets.
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Enum as SQLEnum
import enum

from app.models.base import Base, TimestampMixin


class TemplateCategory(str, enum.Enum):
    """Template category enumeration."""
    OCR = "ocr"
    MANUAL = "manual"
    CUSTOM = "custom"


class Template(Base, TimestampMixin):
    """Template model for reusable text snippets."""

    __tablename__ = "templates"

    name = Column(String(255), nullable=False, index=True)
    category = Column(SQLEnum(TemplateCategory), nullable=False, default=TemplateCategory.MANUAL)
    tags = Column(JSON, nullable=False, default=list)  # List of tag strings
    content = Column(Text, nullable=False)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    # user = relationship("User", back_populates="templates")

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, category={self.category})>"

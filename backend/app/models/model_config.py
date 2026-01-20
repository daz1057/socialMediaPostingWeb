"""
ModelConfig model for AI model configuration.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class ModelConfig(Base, TimestampMixin):
    """ModelConfig model for enabling/disabling AI models."""

    __tablename__ = "model_configs"

    provider = Column(String(50), nullable=False, index=True)
    model_id = Column(String(100), nullable=False)
    model_type = Column(String(20), nullable=False)  # "text" or "image"
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="model_configs")

    # Composite unique index on user_id + provider + model_id + model_type
    __table_args__ = (
        Index("idx_user_model", "user_id", "provider", "model_id", "model_type", unique=True),
    )

    def __repr__(self):
        return f"<ModelConfig(id={self.id}, provider={self.provider}, model_id={self.model_id}, type={self.model_type})>"

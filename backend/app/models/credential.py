"""
Credential model for encrypted API key storage.
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Credential(Base, TimestampMixin):
    """Credential model for storing encrypted API keys."""

    __tablename__ = "credentials"

    key = Column(String(100), nullable=False, index=True)
    encrypted_value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="credentials")

    # Composite unique index on user_id + key
    __table_args__ = (
        Index("idx_user_credential_key", "user_id", "key", unique=True),
    )

    def __repr__(self):
        return f"<Credential(id={self.id}, key={self.key}, user_id={self.user_id})>"

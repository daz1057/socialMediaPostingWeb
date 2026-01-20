"""
CustomerInfo model for storing customer personas.
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class CustomerInfo(Base, TimestampMixin):
    """CustomerInfo model for storing customer persona data."""

    __tablename__ = "customer_info"

    key = Column(String(100), nullable=False, index=True)
    content = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="customer_info")

    # Composite unique index on user_id + key
    __table_args__ = (
        Index("idx_user_customer_key", "user_id", "key", unique=True),
    )

    def __repr__(self):
        return f"<CustomerInfo(id={self.id}, key={self.key}, user_id={self.user_id})>"

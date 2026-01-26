"""
CustomerInfo model for storing customer personas with marketing-focused categories.
"""
import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Index, Enum
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class CustomerCategory(str, enum.Enum):
    """Predefined customer info categories matching desktop app."""
    PAIN = "Pain"
    PLEASURES = "Pleasures"
    DESIRES = "Desires"
    RELATABLE_TRUTHS = "Relatable Truths"
    CUSTOMER_PERSONA = "Customer Persona"
    ARTIST_PERSONA = "Artist Persona"
    BRAND = "Brand"
    IN_GROUPS_AND_OUT_GROUPS = "In Groups and Out Groups"
    PUN_PRIMER = "Pun Primer"
    USP = "USP"
    ROLES = "Roles"


# Categories where ONE random pair is picked during injection
RANDOM_CATEGORIES = {
    CustomerCategory.PAIN,
    CustomerCategory.PLEASURES,
    CustomerCategory.DESIRES,
    CustomerCategory.RELATABLE_TRUTHS,
}

# Categories where ALL pairs are included during injection
ALL_PAIRS_CATEGORIES = {
    CustomerCategory.CUSTOMER_PERSONA,
    CustomerCategory.ARTIST_PERSONA,
    CustomerCategory.BRAND,
    CustomerCategory.IN_GROUPS_AND_OUT_GROUPS,
}

# Categories that are ignored during injection
IGNORED_CATEGORIES = {
    CustomerCategory.PUN_PRIMER,
    CustomerCategory.USP,
    CustomerCategory.ROLES,
}


class CustomerInfo(Base, TimestampMixin):
    """CustomerInfo model for storing customer persona data with prompt-response pairs."""

    __tablename__ = "customer_info"

    category = Column(
        Enum(CustomerCategory, name="customercategory", create_constraint=True),
        nullable=False,
        index=True
    )
    details = Column(JSON, nullable=False, default=list)  # Array of {prompt, response} pairs
    description = Column(Text, nullable=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="customer_info")

    # Composite unique index on user_id + category
    __table_args__ = (
        Index("idx_user_customer_category", "user_id", "category", unique=True),
    )

    def __repr__(self):
        return f"<CustomerInfo(id={self.id}, category={self.category}, user_id={self.user_id})>"

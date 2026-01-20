"""
Base model class with common fields.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer

# Import Base from database module (don't redefine it here)
from app.database import Base


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

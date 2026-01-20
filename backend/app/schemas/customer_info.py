"""
CustomerInfo schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CustomerInfoBase(BaseModel):
    """Base customer info schema."""

    key: str = Field(..., min_length=1, max_length=100, description="Customer info key (e.g., 'Customer Persona')")
    content: Dict[str, Any] = Field(..., description="Customer persona details as JSON")
    description: Optional[str] = Field(None, description="Optional description")


class CustomerInfoCreate(CustomerInfoBase):
    """Schema for creating new customer info."""

    pass


class CustomerInfoUpdate(BaseModel):
    """Schema for updating customer info."""

    content: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class CustomerInfo(CustomerInfoBase):
    """Schema for customer info response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerInfoList(BaseModel):
    """Schema for paginated customer info list response."""

    customer_info: List[CustomerInfo]
    total: int
    skip: int
    limit: int

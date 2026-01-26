"""
CustomerInfo schemas for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CustomerCategory(str, Enum):
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


class InjectionType(str, Enum):
    """How the category is injected into prompts."""
    RANDOM = "random"  # Pick one random pair
    ALL = "all"  # Include all pairs
    IGNORED = "ignored"  # Skip during injection


# Category to injection type mapping
CATEGORY_INJECTION_TYPES = {
    CustomerCategory.PAIN: InjectionType.RANDOM,
    CustomerCategory.PLEASURES: InjectionType.RANDOM,
    CustomerCategory.DESIRES: InjectionType.RANDOM,
    CustomerCategory.RELATABLE_TRUTHS: InjectionType.RANDOM,
    CustomerCategory.CUSTOMER_PERSONA: InjectionType.ALL,
    CustomerCategory.ARTIST_PERSONA: InjectionType.ALL,
    CustomerCategory.BRAND: InjectionType.ALL,
    CustomerCategory.IN_GROUPS_AND_OUT_GROUPS: InjectionType.ALL,
    CustomerCategory.PUN_PRIMER: InjectionType.IGNORED,
    CustomerCategory.USP: InjectionType.IGNORED,
    CustomerCategory.ROLES: InjectionType.IGNORED,
}


class PromptResponsePair(BaseModel):
    """A single prompt-response pair within a category."""
    prompt: str = Field(..., description="The question/prompt")
    response: str = Field(..., description="The answer/response")


class CustomerInfoBase(BaseModel):
    """Base customer info schema."""
    category: CustomerCategory = Field(..., description="Customer info category")
    details: List[PromptResponsePair] = Field(
        default_factory=list,
        description="List of prompt-response pairs"
    )
    description: Optional[str] = Field(None, description="Optional description")


class CustomerInfoCreate(CustomerInfoBase):
    """Schema for creating new customer info."""
    pass


class CustomerInfoUpdate(BaseModel):
    """Schema for updating customer info."""
    details: Optional[List[PromptResponsePair]] = None
    description: Optional[str] = None


class CustomerInfo(CustomerInfoBase):
    """Schema for customer info response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerInfoList(BaseModel):
    """Schema for customer info list response."""
    customer_info: List[CustomerInfo]
    total: int


class CustomerCategoryInfo(BaseModel):
    """Schema for category metadata."""
    category: CustomerCategory
    display_name: str
    injection_type: InjectionType
    description: str


class CustomerCategoriesResponse(BaseModel):
    """Schema for listing all categories with metadata."""
    categories: List[CustomerCategoryInfo]


# Category descriptions for documentation
CATEGORY_DESCRIPTIONS = {
    CustomerCategory.PAIN: "Customer pain points and problems they face",
    CustomerCategory.PLEASURES: "What brings joy and satisfaction to customers",
    CustomerCategory.DESIRES: "Customer wants, goals, and aspirations",
    CustomerCategory.RELATABLE_TRUTHS: "Universal truths your audience relates to",
    CustomerCategory.CUSTOMER_PERSONA: "Detailed customer avatar description",
    CustomerCategory.ARTIST_PERSONA: "Your brand's creative voice and personality",
    CustomerCategory.BRAND: "Core brand values and messaging",
    CustomerCategory.IN_GROUPS_AND_OUT_GROUPS: "Who your brand serves vs. who it doesn't",
    CustomerCategory.PUN_PRIMER: "Wordplay and puns related to your brand",
    CustomerCategory.USP: "Unique Selling Proposition",
    CustomerCategory.ROLES: "Roles and personas in content creation",
}

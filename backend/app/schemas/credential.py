"""
Credential schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CredentialBase(BaseModel):
    """Base credential schema."""

    key: str = Field(..., min_length=1, max_length=100, description="Credential key (e.g., 'openai_api_key')")
    description: Optional[str] = Field(None, description="Optional description of this credential")


class CredentialCreate(CredentialBase):
    """Schema for creating a new credential."""

    value: str = Field(..., min_length=1, description="Plain text API key or credential value")


class CredentialUpdate(BaseModel):
    """Schema for updating a credential."""

    value: str = Field(..., min_length=1, description="New plain text API key or credential value")
    description: Optional[str] = None


class Credential(CredentialBase):
    """Schema for credential response (NEVER includes value!)."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CredentialList(BaseModel):
    """Schema for paginated credential list response."""

    credentials: List[Credential]
    total: int
    skip: int
    limit: int


class CredentialValidateRequest(BaseModel):
    """Schema for validating a credential with a provider."""

    key: str = Field(..., description="Credential key to validate")
    provider: str = Field(..., description="Provider name (e.g., 'openai', 'anthropic')")
    model_id: str = Field(..., description="Model ID to test with")


class CredentialValidateResponse(BaseModel):
    """Schema for credential validation response."""

    key: str
    provider: str
    is_valid: bool
    message: str

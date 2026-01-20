"""
Token schemas for JWT authentication.
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: Optional[int] = None  # user_id
    exp: Optional[int] = None  # expiration timestamp

"""
Credentials API endpoints for encrypted credential management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.credential import Credential
from app.schemas.credential import (
    CredentialCreate,
    CredentialUpdate,
    Credential as CredentialSchema,
    CredentialList,
    CredentialValidateRequest,
    CredentialValidateResponse,
)
from app.utils.security import get_current_active_user
from app.utils.encryption import encrypt_value, decrypt_value
from app.providers import ProviderFactory

router = APIRouter()


@router.get("/", response_model=CredentialList)
async def list_credentials(
    skip: int = Query(0, ge=0, description="Number of credentials to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of credentials to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all credentials for the current user (values NOT included).

    Args:
        skip: Number of credentials to skip (pagination)
        limit: Maximum number of credentials to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        CredentialList: List of credentials (without values)
    """
    # Build query
    query = select(Credential).filter(Credential.user_id == current_user.id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and execute
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    credentials = result.scalars().all()

    return CredentialList(
        credentials=credentials,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=CredentialSchema, status_code=status.HTTP_201_CREATED)
async def create_credential(
    credential_in: CredentialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new credential with encryption.

    Args:
        credential_in: Credential creation data (with plain value)
        db: Database session
        current_user: Current authenticated user

    Returns:
        CredentialSchema: Created credential (without value)

    Raises:
        HTTPException: If credential key already exists for user or encryption fails
    """
    # Check if credential already exists
    result = await db.execute(
        select(Credential).filter(
            Credential.user_id == current_user.id,
            Credential.key == credential_in.key,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Credential with key '{credential_in.key}' already exists",
        )

    # Encrypt the value
    try:
        encrypted_value = encrypt_value(credential_in.value)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption failed: {str(e)}",
        )

    # Create credential
    credential = Credential(
        key=credential_in.key,
        encrypted_value=encrypted_value,
        description=credential_in.description,
        user_id=current_user.id,
    )

    db.add(credential)
    await db.commit()
    await db.refresh(credential)

    return credential


@router.get("/{key}", response_model=CredentialSchema)
async def get_credential(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific credential by key (value NOT included).

    Args:
        key: Credential key
        db: Database session
        current_user: Current authenticated user

    Returns:
        CredentialSchema: Credential details (without value)

    Raises:
        HTTPException: If credential not found or unauthorized
    """
    result = await db.execute(
        select(Credential).filter(
            Credential.user_id == current_user.id,
            Credential.key == key,
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    return credential


@router.put("/{key}", response_model=CredentialSchema)
async def update_credential(
    key: str,
    credential_in: CredentialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a credential's value (re-encrypts).

    Args:
        key: Credential key
        credential_in: Credential update data (with new plain value)
        db: Database session
        current_user: Current authenticated user

    Returns:
        CredentialSchema: Updated credential (without value)

    Raises:
        HTTPException: If credential not found, unauthorized, or encryption fails
    """
    # Get existing credential
    result = await db.execute(
        select(Credential).filter(
            Credential.user_id == current_user.id,
            Credential.key == key,
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    # Encrypt the new value
    try:
        encrypted_value = encrypt_value(credential_in.value)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption failed: {str(e)}",
        )

    # Update credential
    credential.encrypted_value = encrypted_value
    if credential_in.description is not None:
        credential.description = credential_in.description

    await db.commit()
    await db.refresh(credential)

    return credential


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a credential.

    Args:
        key: Credential key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If credential not found or unauthorized
    """
    # Get existing credential
    result = await db.execute(
        select(Credential).filter(
            Credential.user_id == current_user.id,
            Credential.key == key,
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    await db.delete(credential)
    await db.commit()

    return None


@router.post("/validate", response_model=CredentialValidateResponse)
async def validate_credential(
    request: CredentialValidateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Validate a credential by testing it with the specified provider.

    Args:
        request: Validation request (key, provider, model_id)
        db: Database session
        current_user: Current authenticated user

    Returns:
        CredentialValidateResponse: Validation result

    Raises:
        HTTPException: If credential not found or provider not available
    """
    # Get credential
    result = await db.execute(
        select(Credential).filter(
            Credential.user_id == current_user.id,
            Credential.key == request.key,
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    # Decrypt credential
    try:
        api_key = decrypt_value(credential.encrypted_value)
    except Exception as e:
        return CredentialValidateResponse(
            key=request.key,
            provider=request.provider,
            is_valid=False,
            message=f"Decryption failed: {str(e)}",
        )

    # Create provider instance
    provider = ProviderFactory.create_text_provider(
        provider_name=request.provider,
        api_key=api_key,
        model_id=request.model_id,
    )

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{request.provider}' not found",
        )

    # Validate credentials
    try:
        is_valid = provider.validate_credentials()
        message = "Credentials are valid" if is_valid else "Credentials are invalid"
    except Exception as e:
        is_valid = False
        message = f"Validation failed: {str(e)}"

    return CredentialValidateResponse(
        key=request.key,
        provider=request.provider,
        is_valid=is_valid,
        message=message,
    )

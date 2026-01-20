"""
ModelConfig API endpoints for managing AI model configurations.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.model_config import ModelConfig
from app.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfig as ModelConfigSchema,
    ModelConfigList,
    ProviderInfo,
    ProvidersListResponse,
)
from app.utils.security import get_current_active_user
from app.providers import ProviderFactory

router = APIRouter()


@router.get("/", response_model=ModelConfigList)
async def list_model_configs(
    skip: int = Query(0, ge=0, description="Number of models to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of models to return"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model_type: Optional[str] = Query(None, description="Filter by type (text/image)"),
    enabled_only: bool = Query(False, description="Show only enabled models"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all model configurations for the current user.

    Args:
        skip: Number of models to skip (pagination)
        limit: Maximum number of models to return
        provider: Optional provider filter
        model_type: Optional type filter (text/image)
        enabled_only: Only show enabled models
        db: Database session
        current_user: Current authenticated user

    Returns:
        ModelConfigList: List of model configurations
    """
    # Build query
    query = select(ModelConfig).filter(ModelConfig.user_id == current_user.id)

    # Apply filters
    if provider:
        query = query.filter(ModelConfig.provider == provider)
    if model_type:
        query = query.filter(ModelConfig.model_type == model_type)
    if enabled_only:
        query = query.filter(ModelConfig.is_enabled == True)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and execute
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    models = result.scalars().all()

    return ModelConfigList(
        models=models,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=ModelConfigSchema, status_code=status.HTTP_201_CREATED)
async def create_model_config(
    model_config_in: ModelConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Enable a model for the current user.

    Args:
        model_config_in: Model configuration data
        db: Database session
        current_user: Current authenticated user

    Returns:
        ModelConfigSchema: Created model configuration

    Raises:
        HTTPException: If model config already exists or provider/model not available
    """
    # Check if model config already exists
    result = await db.execute(
        select(ModelConfig).filter(
            ModelConfig.user_id == current_user.id,
            ModelConfig.provider == model_config_in.provider,
            ModelConfig.model_id == model_config_in.model_id,
            ModelConfig.model_type == model_config_in.model_type,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model config for {model_config_in.provider}/{model_config_in.model_id} already exists",
        )

    # Validate provider and model exist
    available_models = ProviderFactory.get_models_for_provider(
        model_config_in.provider,
        model_config_in.model_type
    )
    if not available_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{model_config_in.provider}' not found or has no models",
        )

    # Check if model_id is valid for this provider
    if model_config_in.model_id not in available_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{model_config_in.model_id}' not available for provider '{model_config_in.provider}'",
        )

    # If setting as default, unset other defaults
    if model_config_in.is_default:
        result = await db.execute(
            select(ModelConfig).filter(
                ModelConfig.user_id == current_user.id,
                ModelConfig.model_type == model_config_in.model_type,
                ModelConfig.is_default == True,
            )
        )
        current_defaults = result.scalars().all()
        for default_model in current_defaults:
            default_model.is_default = False

    # Create model config
    model_config = ModelConfig(
        **model_config_in.model_dump(),
        user_id=current_user.id,
    )

    db.add(model_config)
    await db.commit()
    await db.refresh(model_config)

    return model_config


@router.get("/{model_config_id}", response_model=ModelConfigSchema)
async def get_model_config(
    model_config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific model configuration.

    Args:
        model_config_id: Model configuration ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        ModelConfigSchema: Model configuration details

    Raises:
        HTTPException: If model config not found or unauthorized
    """
    result = await db.execute(
        select(ModelConfig).filter(
            ModelConfig.id == model_config_id,
            ModelConfig.user_id == current_user.id,
        )
    )
    model_config = result.scalar_one_or_none()

    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model configuration not found",
        )

    return model_config


@router.put("/{model_config_id}", response_model=ModelConfigSchema)
async def update_model_config(
    model_config_id: int,
    model_config_in: ModelConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a model configuration (enable/disable, set as default).

    Args:
        model_config_id: Model configuration ID
        model_config_in: Model configuration update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        ModelConfigSchema: Updated model configuration

    Raises:
        HTTPException: If model config not found or unauthorized
    """
    # Get existing model config
    result = await db.execute(
        select(ModelConfig).filter(
            ModelConfig.id == model_config_id,
            ModelConfig.user_id == current_user.id,
        )
    )
    model_config = result.scalar_one_or_none()

    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model configuration not found",
        )

    # If setting as default, unset other defaults
    if model_config_in.is_default is True:
        result = await db.execute(
            select(ModelConfig).filter(
                ModelConfig.user_id == current_user.id,
                ModelConfig.model_type == model_config.model_type,
                ModelConfig.is_default == True,
                ModelConfig.id != model_config_id,
            )
        )
        current_defaults = result.scalars().all()
        for default_model in current_defaults:
            default_model.is_default = False

    # Update fields
    update_data = model_config_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model_config, field, value)

    await db.commit()
    await db.refresh(model_config)

    return model_config


@router.delete("/{model_config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_config(
    model_config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a model configuration.

    Args:
        model_config_id: Model configuration ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If model config not found or unauthorized
    """
    # Get existing model config
    result = await db.execute(
        select(ModelConfig).filter(
            ModelConfig.id == model_config_id,
            ModelConfig.user_id == current_user.id,
        )
    )
    model_config = result.scalar_one_or_none()

    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model configuration not found",
        )

    await db.delete(model_config)
    await db.commit()

    return None


@router.get("/providers/list", response_model=ProvidersListResponse)
async def list_providers(
    current_user: User = Depends(get_current_active_user),
):
    """
    List all available providers and their models.

    Args:
        current_user: Current authenticated user

    Returns:
        ProvidersListResponse: All text and image providers with their models
    """
    # Get text providers
    text_providers = []
    for provider_name in ProviderFactory.get_available_text_providers():
        provider_class = ProviderFactory.get_text_provider_class(provider_name)
        if provider_class:
            text_providers.append(
                ProviderInfo(
                    name=provider_name,
                    available_models=provider_class.get_available_models(),
                    valid_credential_keys=provider_class.get_valid_credential_keys(),
                )
            )

    # Get image providers
    image_providers = []
    for provider_name in ProviderFactory.get_available_image_providers():
        provider_class = ProviderFactory.get_image_provider_class(provider_name)
        if provider_class:
            image_providers.append(
                ProviderInfo(
                    name=provider_name,
                    available_models=provider_class.get_available_models(),
                    valid_credential_keys=provider_class.get_valid_credential_keys(),
                )
            )

    return ProvidersListResponse(
        text_providers=text_providers,
        image_providers=image_providers,
    )

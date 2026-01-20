"""
Templates CRUD endpoints for reusable text snippets.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.template import TemplateCategory as ModelTemplateCategory
from app.schemas.template import (
    TemplateCreate, TemplateUpdate, Template as TemplateSchema, TemplateList,
    TemplateCategory
)
from app.services.template_service import TemplateService
from app.utils.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=TemplateList)
async def list_templates(
    skip: int = Query(0, ge=0, description="Number of templates to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of templates to return"),
    category: Optional[TemplateCategory] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in name and content"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List templates with optional filtering and pagination.

    Args:
        skip: Number of templates to skip (pagination)
        limit: Maximum number of templates to return
        category: Optional category filter (ocr, manual, custom)
        tag: Optional tag filter
        search: Optional name/content search query
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateList: List of templates with pagination info
    """
    service = TemplateService(db)

    # Convert schema enum to model enum if provided
    model_category = ModelTemplateCategory(category.value) if category else None

    templates, total = await service.list_templates(
        user_id=current_user.id,
        category=model_category,
        tag=tag,
        search=search,
        skip=skip,
        limit=limit,
    )

    return TemplateList(
        templates=templates,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=TemplateSchema, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_in: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new template.

    Args:
        template_in: Template creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateSchema: Created template
    """
    service = TemplateService(db)
    template = await service.create_template(
        user_id=current_user.id,
        template_data=template_in,
    )
    return template


@router.get("/tags", response_model=List[str])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all unique tags used in user's templates.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of unique tag strings
    """
    service = TemplateService(db)
    tags = await service.get_all_tags(current_user.id)
    return tags


@router.get("/{template_id}", response_model=TemplateSchema)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific template by ID.

    Args:
        template_id: Template ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateSchema: Template details

    Raises:
        HTTPException: If template not found
    """
    service = TemplateService(db)
    template = await service.get_template(current_user.id, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    return template


@router.put("/{template_id}", response_model=TemplateSchema)
async def update_template(
    template_id: int,
    template_in: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a template.

    Args:
        template_id: Template ID
        template_in: Template update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateSchema: Updated template

    Raises:
        HTTPException: If template not found
    """
    service = TemplateService(db)
    template = await service.update_template(
        user_id=current_user.id,
        template_id=template_id,
        template_data=template_in,
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a template.

    Args:
        template_id: Template ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If template not found
    """
    service = TemplateService(db)
    deleted = await service.delete_template(current_user.id, template_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    return None

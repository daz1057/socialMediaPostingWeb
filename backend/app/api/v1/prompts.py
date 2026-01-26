"""
Prompt CRUD endpoints for managing AI generation templates.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate, Prompt as PromptSchema, PromptList
from app.utils.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=PromptList)
async def list_prompts(
    skip: int = Query(0, ge=0, description="Number of prompts to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of prompts to return"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    search: Optional[str] = Query(None, description="Search in prompt name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List prompts with optional filtering and pagination.

    Args:
        skip: Number of prompts to skip (pagination)
        limit: Maximum number of prompts to return
        tag_id: Optional tag ID filter
        search: Optional search query for prompt name
        db: Database session
        current_user: Current authenticated user

    Returns:
        PromptList: List of prompts with pagination info
    """
    # Build query with eager loading of tag relationship
    query = select(Prompt).options(selectinload(Prompt.tag)).filter(Prompt.user_id == current_user.id)

    # Apply filters
    if tag_id is not None:
        query = query.filter(Prompt.tag_id == tag_id)

    if search:
        query = query.filter(Prompt.name.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and execute
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    prompts = result.scalars().all()

    return PromptList(
        prompts=prompts,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=PromptSchema, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_in: PromptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new prompt.

    Args:
        prompt_in: Prompt creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        PromptSchema: Created prompt
    """
    # Create prompt
    prompt = Prompt(
        **prompt_in.model_dump(),
        user_id=current_user.id,
    )

    db.add(prompt)
    await db.commit()

    # Re-fetch with tag relationship loaded
    result = await db.execute(
        select(Prompt).options(selectinload(Prompt.tag)).filter(Prompt.id == prompt.id)
    )
    prompt = result.scalar_one()

    return prompt


@router.get("/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific prompt by ID.

    Args:
        prompt_id: Prompt ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PromptSchema: Prompt details

    Raises:
        HTTPException: If prompt not found or unauthorized
    """
    result = await db.execute(
        select(Prompt).options(selectinload(Prompt.tag)).filter(
            Prompt.id == prompt_id,
            Prompt.user_id == current_user.id,
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    return prompt


@router.put("/{prompt_id}", response_model=PromptSchema)
async def update_prompt(
    prompt_id: int,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a prompt.

    Args:
        prompt_id: Prompt ID
        prompt_in: Prompt update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        PromptSchema: Updated prompt

    Raises:
        HTTPException: If prompt not found or unauthorized
    """
    # Get existing prompt
    result = await db.execute(
        select(Prompt).options(selectinload(Prompt.tag)).filter(
            Prompt.id == prompt_id,
            Prompt.user_id == current_user.id,
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    # Update fields
    update_data = prompt_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    await db.commit()

    # Re-fetch with tag relationship after update (tag_id may have changed)
    result = await db.execute(
        select(Prompt).options(selectinload(Prompt.tag)).filter(Prompt.id == prompt_id)
    )
    prompt = result.scalar_one()

    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a prompt.

    Args:
        prompt_id: Prompt ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If prompt not found or unauthorized
    """
    # Get existing prompt
    result = await db.execute(
        select(Prompt).filter(
            Prompt.id == prompt_id,
            Prompt.user_id == current_user.id,
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    await db.delete(prompt)
    await db.commit()

    return None

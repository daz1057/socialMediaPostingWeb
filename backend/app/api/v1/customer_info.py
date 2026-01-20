"""
CustomerInfo API endpoints for managing customer personas.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.customer_info import CustomerInfo
from app.schemas.customer_info import (
    CustomerInfoCreate,
    CustomerInfoUpdate,
    CustomerInfo as CustomerInfoSchema,
    CustomerInfoList,
)
from app.utils.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=CustomerInfoList)
async def list_customer_info(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of items to return"),
    search: Optional[str] = Query(None, description="Search in key"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all customer info for the current user.

    Args:
        skip: Number of items to skip (pagination)
        limit: Maximum number of items to return
        search: Optional search query for key
        db: Database session
        current_user: Current authenticated user

    Returns:
        CustomerInfoList: List of customer info items
    """
    # Build query
    query = select(CustomerInfo).filter(CustomerInfo.user_id == current_user.id)

    # Apply search filter
    if search:
        query = query.filter(CustomerInfo.key.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and execute
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    customer_info = result.scalars().all()

    return CustomerInfoList(
        customer_info=customer_info,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=CustomerInfoSchema, status_code=status.HTTP_201_CREATED)
async def create_customer_info(
    customer_info_in: CustomerInfoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new customer info.

    Args:
        customer_info_in: Customer info creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CustomerInfoSchema: Created customer info

    Raises:
        HTTPException: If customer info key already exists for user
    """
    # Check if key already exists
    result = await db.execute(
        select(CustomerInfo).filter(
            CustomerInfo.user_id == current_user.id,
            CustomerInfo.key == customer_info_in.key,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer info with key '{customer_info_in.key}' already exists",
        )

    # Create customer info
    customer_info = CustomerInfo(
        **customer_info_in.model_dump(),
        user_id=current_user.id,
    )

    db.add(customer_info)
    await db.commit()
    await db.refresh(customer_info)

    return customer_info


@router.get("/{key}", response_model=CustomerInfoSchema)
async def get_customer_info(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get specific customer info by key.

    Args:
        key: Customer info key
        db: Database session
        current_user: Current authenticated user

    Returns:
        CustomerInfoSchema: Customer info details

    Raises:
        HTTPException: If customer info not found or unauthorized
    """
    result = await db.execute(
        select(CustomerInfo).filter(
            CustomerInfo.user_id == current_user.id,
            CustomerInfo.key == key,
        )
    )
    customer_info = result.scalar_one_or_none()

    if not customer_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer info not found",
        )

    return customer_info


@router.put("/{key}", response_model=CustomerInfoSchema)
async def update_customer_info(
    key: str,
    customer_info_in: CustomerInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update customer info.

    Args:
        key: Customer info key
        customer_info_in: Customer info update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CustomerInfoSchema: Updated customer info

    Raises:
        HTTPException: If customer info not found or unauthorized
    """
    # Get existing customer info
    result = await db.execute(
        select(CustomerInfo).filter(
            CustomerInfo.user_id == current_user.id,
            CustomerInfo.key == key,
        )
    )
    customer_info = result.scalar_one_or_none()

    if not customer_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer info not found",
        )

    # Update fields
    update_data = customer_info_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer_info, field, value)

    await db.commit()
    await db.refresh(customer_info)

    return customer_info


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_info(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete customer info.

    Args:
        key: Customer info key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If customer info not found or unauthorized
    """
    # Get existing customer info
    result = await db.execute(
        select(CustomerInfo).filter(
            CustomerInfo.user_id == current_user.id,
            CustomerInfo.key == key,
        )
    )
    customer_info = result.scalar_one_or_none()

    if not customer_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer info not found",
        )

    await db.delete(customer_info)
    await db.commit()

    return None

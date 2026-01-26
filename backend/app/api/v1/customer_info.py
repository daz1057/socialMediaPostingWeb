"""
CustomerInfo API endpoints for managing customer personas with predefined categories.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.customer_info import CustomerInfo, CustomerCategory as ModelCategory
from app.schemas.customer_info import (
    CustomerInfoUpdate,
    CustomerInfo as CustomerInfoSchema,
    CustomerInfoList,
    CustomerCategory,
    CustomerCategoryInfo,
    CustomerCategoriesResponse,
    InjectionType,
    CATEGORY_INJECTION_TYPES,
    CATEGORY_DESCRIPTIONS,
    PromptResponsePair,
)
from app.utils.security import get_current_active_user

router = APIRouter()


@router.get("/categories", response_model=CustomerCategoriesResponse)
async def list_categories(
    current_user: User = Depends(get_current_active_user),
):
    """
    List all available customer info categories with their injection rules.

    Returns:
        CustomerCategoriesResponse: List of all 11 categories with metadata
    """
    categories = []
    for category in CustomerCategory:
        categories.append(
            CustomerCategoryInfo(
                category=category,
                display_name=category.value,
                injection_type=CATEGORY_INJECTION_TYPES[category],
                description=CATEGORY_DESCRIPTIONS[category],
            )
        )
    return CustomerCategoriesResponse(categories=categories)


@router.post("/initialize", response_model=CustomerInfoList)
async def initialize_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Initialize all customer info categories for a new user.
    Creates empty entries for all 11 predefined categories.

    Returns:
        CustomerInfoList: List of created customer info entries
    """
    created = []

    for category in CustomerCategory:
        # Check if already exists
        result = await db.execute(
            select(CustomerInfo).filter(
                CustomerInfo.user_id == current_user.id,
                CustomerInfo.category == ModelCategory(category.value),
            )
        )
        existing = result.scalar_one_or_none()

        if not existing:
            customer_info = CustomerInfo(
                category=ModelCategory(category.value),
                details=[],
                user_id=current_user.id,
            )
            db.add(customer_info)
            created.append(customer_info)

    if created:
        await db.commit()
        for item in created:
            await db.refresh(item)

    # Return all categories for the user
    result = await db.execute(
        select(CustomerInfo).filter(CustomerInfo.user_id == current_user.id)
    )
    all_items = result.scalars().all()

    return CustomerInfoList(
        customer_info=all_items,
        total=len(all_items),
    )


@router.get("/", response_model=CustomerInfoList)
async def list_customer_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all customer info for the current user.

    Returns:
        CustomerInfoList: List of customer info items
    """
    result = await db.execute(
        select(CustomerInfo).filter(CustomerInfo.user_id == current_user.id)
    )
    customer_info = result.scalars().all()

    return CustomerInfoList(
        customer_info=customer_info,
        total=len(customer_info),
    )


@router.get("/{category}", response_model=CustomerInfoSchema)
async def get_customer_info(
    category: CustomerCategory,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get specific customer info by category.

    Args:
        category: Customer info category
        db: Database session
        current_user: Current authenticated user

    Returns:
        CustomerInfoSchema: Customer info details

    Raises:
        HTTPException: If customer info not found
    """
    result = await db.execute(
        select(CustomerInfo).filter(
            CustomerInfo.user_id == current_user.id,
            CustomerInfo.category == ModelCategory(category.value),
        )
    )
    customer_info = result.scalar_one_or_none()

    if not customer_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer info for category '{category.value}' not found. Please initialize categories first.",
        )

    return customer_info


@router.put("/{category}", response_model=CustomerInfoSchema)
async def update_customer_info(
    category: CustomerCategory,
    customer_info_in: CustomerInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update or create customer info for a category (upsert behavior).

    Args:
        category: Customer info category
        customer_info_in: Customer info update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CustomerInfoSchema: Updated customer info
    """
    # Get existing customer info or create new
    result = await db.execute(
        select(CustomerInfo).filter(
            CustomerInfo.user_id == current_user.id,
            CustomerInfo.category == ModelCategory(category.value),
        )
    )
    customer_info = result.scalar_one_or_none()

    if not customer_info:
        # Create new entry
        customer_info = CustomerInfo(
            category=ModelCategory(category.value),
            details=[],
            user_id=current_user.id,
        )
        db.add(customer_info)

    # Update fields
    update_data = customer_info_in.model_dump(exclude_unset=True)

    # Convert PromptResponsePair objects to dicts for JSON storage
    if "details" in update_data and update_data["details"] is not None:
        update_data["details"] = [
            pair.model_dump() if isinstance(pair, PromptResponsePair) else pair
            for pair in update_data["details"]
        ]

    for field, value in update_data.items():
        setattr(customer_info, field, value)

    await db.commit()
    await db.refresh(customer_info)

    return customer_info

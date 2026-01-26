"""
Import API endpoint for migrating data from desktop app JSON files.
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict

from app.database import get_db
from app.models.user import User
from app.models.prompt import Prompt
from app.models.tag import Tag
from app.models.customer_info import CustomerInfo, CustomerCategory
from app.utils.security import get_current_active_user

router = APIRouter()


class ImportResult(BaseModel):
    """Result of import operation."""
    success: bool
    tags_imported: int = 0
    customer_info_imported: int = 0
    prompts_imported: int = 0
    errors: List[str] = []


class DesktopTag(BaseModel):
    """Tag structure from desktop app."""
    model_config = ConfigDict(extra="ignore")
    name: str


class DesktopPromptResponsePair(BaseModel):
    """Prompt-response pair from desktop app."""
    model_config = ConfigDict(extra="ignore")
    prompt: str
    response: str


class DesktopCustomerInfo(BaseModel):
    """Customer info structure from desktop app."""
    model_config = ConfigDict(extra="ignore")
    name: str
    details: str  # JSON string containing array of prompt-response pairs


class DesktopPrompt(BaseModel):
    """Prompt structure from desktop app."""
    model_config = ConfigDict(extra="ignore")
    name: str
    details: str
    selected_customers: dict = {}
    url: Optional[str] = None
    media_file_path: Optional[str] = None
    aws_folder_url: Optional[str] = None
    artwork_description: Optional[str] = None
    tag: Optional[str] = None
    example_image: Optional[str] = None


class ImportRequest(BaseModel):
    """Request body for import."""
    tags: Optional[List[DesktopTag]] = None
    customer_info: Optional[List[DesktopCustomerInfo]] = None
    prompts: Optional[List[DesktopPrompt]] = None


# Map desktop category names to our enum
CATEGORY_MAP = {
    "Customer Persona": CustomerCategory.CUSTOMER_PERSONA,
    "Pleasures": CustomerCategory.PLEASURES,
    "Artist Persona": CustomerCategory.ARTIST_PERSONA,
    "Brand": CustomerCategory.BRAND,
    "Desires": CustomerCategory.DESIRES,
    "In Groups and Out Groups": CustomerCategory.IN_GROUPS_AND_OUT_GROUPS,
    "Pain": CustomerCategory.PAIN,
    "Pun Primer": CustomerCategory.PUN_PRIMER,
    "Relatable Truths": CustomerCategory.RELATABLE_TRUTHS,
    "USP": CustomerCategory.USP,
    "Roles": CustomerCategory.ROLES,
}


@router.post("/", response_model=ImportResult)
async def import_data(
    import_request: ImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Import data from desktop app JSON format.

    Accepts:
    - tags: Array of {name: string}
    - customer_info: Array of {name: string, details: JSON string of [{prompt, response}]}
    - prompts: Array of desktop prompt objects

    Returns import results with counts and any errors.
    """
    result = ImportResult(success=True)
    tag_name_to_id = {}

    try:
        # 1. Import tags first (prompts reference them)
        # Note: Tags are shared across all users (no user_id)
        if import_request.tags:
            for tag_data in import_request.tags:
                try:
                    # Check if tag exists (tags are global, not user-specific)
                    existing = await db.execute(
                        select(Tag).filter(Tag.name == tag_data.name)
                    )
                    tag = existing.scalar_one_or_none()

                    if not tag:
                        tag = Tag(name=tag_data.name)
                        db.add(tag)
                        await db.flush()
                        result.tags_imported += 1

                    tag_name_to_id[tag_data.name] = tag.id
                except Exception as e:
                    result.errors.append(f"Tag '{tag_data.name}': {str(e)}")

        # Also load existing tags into the map (tags are global)
        existing_tags = await db.execute(select(Tag))
        for tag in existing_tags.scalars().all():
            tag_name_to_id[tag.name] = tag.id

        # 2. Import customer info
        if import_request.customer_info:
            for ci_data in import_request.customer_info:
                try:
                    # Map category name to enum
                    category = CATEGORY_MAP.get(ci_data.name)
                    if not category:
                        result.errors.append(f"Customer info '{ci_data.name}': Unknown category")
                        continue

                    # Parse the details JSON string
                    try:
                        details_array = json.loads(ci_data.details) if ci_data.details else []
                    except json.JSONDecodeError:
                        details_array = []
                        result.errors.append(f"Customer info '{ci_data.name}': Invalid JSON in details")

                    # Check if exists, update or create
                    existing = await db.execute(
                        select(CustomerInfo).filter(
                            CustomerInfo.user_id == current_user.id,
                            CustomerInfo.category == category,
                        )
                    )
                    customer_info = existing.scalar_one_or_none()

                    if customer_info:
                        customer_info.details = details_array
                    else:
                        customer_info = CustomerInfo(
                            category=category,
                            details=details_array,
                            user_id=current_user.id,
                        )
                        db.add(customer_info)

                    result.customer_info_imported += 1
                except Exception as e:
                    result.errors.append(f"Customer info '{ci_data.name}': {str(e)}")

        # 3. Import prompts
        if import_request.prompts:
            for prompt_data in import_request.prompts:
                try:
                    # Check if prompt with same name exists
                    existing = await db.execute(
                        select(Prompt).filter(
                            Prompt.user_id == current_user.id,
                            Prompt.name == prompt_data.name,
                        )
                    )
                    prompt = existing.scalar_one_or_none()

                    # Get tag ID if specified
                    tag_id = None
                    if prompt_data.tag and prompt_data.tag in tag_name_to_id:
                        tag_id = tag_name_to_id[prompt_data.tag]

                    if prompt:
                        # Update existing prompt
                        prompt.details = prompt_data.details
                        prompt.selected_customers = prompt_data.selected_customers
                        prompt.url = prompt_data.url or ""
                        prompt.media_file_path = prompt_data.media_file_path or ""
                        prompt.aws_folder_url = prompt_data.aws_folder_url or ""
                        prompt.artwork_description = prompt_data.artwork_description or ""
                        prompt.example_image = prompt_data.example_image or ""
                        prompt.tag_id = tag_id
                    else:
                        # Create new prompt
                        prompt = Prompt(
                            name=prompt_data.name,
                            details=prompt_data.details,
                            selected_customers=prompt_data.selected_customers,
                            url=prompt_data.url or "",
                            media_file_path=prompt_data.media_file_path or "",
                            aws_folder_url=prompt_data.aws_folder_url or "",
                            artwork_description=prompt_data.artwork_description or "",
                            example_image=prompt_data.example_image or "",
                            tag_id=tag_id,
                            user_id=current_user.id,
                        )
                        db.add(prompt)

                    result.prompts_imported += 1
                except Exception as e:
                    result.errors.append(f"Prompt '{prompt_data.name}': {str(e)}")

        await db.commit()

        if result.errors:
            result.success = len(result.errors) < (
                (len(import_request.tags or []) +
                 len(import_request.customer_info or []) +
                 len(import_request.prompts or [])) / 2
            )

        return result

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.post("/files", response_model=ImportResult)
async def import_from_files(
    tags_file: Optional[UploadFile] = File(None),
    customer_info_file: Optional[UploadFile] = File(None),
    prompts_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Import data from uploaded JSON files.

    Accepts multipart form with:
    - tags_file: tags.json file
    - customer_info_file: customer_info.json file
    - prompts_file: prompts.json file
    """
    import_request = ImportRequest()

    try:
        if tags_file:
            content = await tags_file.read()
            import_request.tags = [DesktopTag(**t) for t in json.loads(content)]

        if customer_info_file:
            content = await customer_info_file.read()
            import_request.customer_info = [DesktopCustomerInfo(**ci) for ci in json.loads(content)]

        if prompts_file:
            content = await prompts_file.read()
            import_request.prompts = [DesktopPrompt(**p) for p in json.loads(content)]

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON in uploaded file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing uploaded files: {str(e)}"
        )

    return await import_data(import_request, db, current_user)

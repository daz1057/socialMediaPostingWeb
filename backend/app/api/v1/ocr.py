"""
OCR API endpoints for text extraction from images.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.ocr import (
    OCRProcessResponse,
    OCRProviderInfo,
    OCRProvidersResponse,
)
from app.utils.security import get_current_active_user
from app.services.ocr_service import OCRService
from app.providers import ProviderFactory

router = APIRouter()


@router.post("/process", response_model=OCRProcessResponse)
async def process_image(
    file: UploadFile = File(..., description="Image file to process"),
    model_config_id: int = Form(..., description="Vision model configuration ID"),
    custom_prompt: Optional[str] = Form(None, description="Custom extraction prompt"),
    template_name: Optional[str] = Form(None, max_length=255, description="Name for OCR template"),
    template_tags: Optional[str] = Form(None, description="Comma-separated tags for template"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Process an image and extract text using a vision model.

    The extracted text will be returned and optionally saved as an OCR template.

    Args:
        file: Image file (PNG, JPG, GIF, WEBP)
        model_config_id: ID of the vision model configuration to use
        custom_prompt: Optional custom prompt for text extraction
        template_name: Optional name for the created template
        template_tags: Optional comma-separated tags for the template

    Returns:
        OCRProcessResponse: Extracted text and template info
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # Read file content
    try:
        image_data = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read image file: {str(e)}",
        )

    # Parse tags
    tags: Optional[List[str]] = None
    if template_tags:
        tags = [t.strip() for t in template_tags.split(",") if t.strip()]

    # Process image
    ocr_service = OCRService(db)

    try:
        response, template = await ocr_service.process_image(
            user=current_user,
            image_data=image_data,
            image_filename=file.filename or "image.png",
            model_config_id=model_config_id,
            custom_prompt=custom_prompt,
            template_name=template_name,
            template_tags=tags,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return OCRProcessResponse(
        extracted_text=response.extracted_text,
        model_used=response.model_used,
        provider=response.provider,
        usage=response.usage,
        request_id=response.request_id,
        success=response.success,
        error=response.error,
        template_id=template.id if template else None,
        template_name=template.name if template else None,
    )


@router.get("/providers", response_model=OCRProvidersResponse)
async def list_ocr_providers(
    current_user: User = Depends(get_current_active_user),
):
    """
    List all available OCR/vision providers and their models.

    Returns:
        OCRProvidersResponse: List of available vision providers
    """
    providers = []

    for provider_name in ProviderFactory.get_available_vision_providers():
        provider_class = ProviderFactory.get_vision_provider_class(provider_name)
        if provider_class:
            # Determine if this is a local provider (no credentials required)
            valid_keys = provider_class.get_valid_credential_keys()
            is_local = len(valid_keys) == 0

            # Generate display name
            display_name = provider_name.replace("_", " ").title()
            if "lm_studio" in provider_name:
                display_name = "LM Studio (Local)"
            elif "openai" in provider_name:
                display_name = "OpenAI GPT-4 Vision"
            elif "anthropic" in provider_name:
                display_name = "Anthropic Claude Vision"

            providers.append(
                OCRProviderInfo(
                    name=provider_name,
                    display_name=display_name,
                    available_models=provider_class.get_available_models(),
                    valid_credential_keys=valid_keys,
                    is_local=is_local,
                )
            )

    return OCRProvidersResponse(providers=providers)

"""
Text and image generation API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.generation import TextGenerationRequest, TextGenerationResponse
from app.schemas.image_generation import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageGenerationError,
    ImageData,
    ReferenceImageUploadResponse,
)
from app.utils.security import get_current_active_user
from app.services.generation_service import GenerationService
from app.services.image_generation_service import ImageGenerationService
from app.services.s3_service import get_s3_service

router = APIRouter()


@router.post("/text", response_model=TextGenerationResponse)
async def generate_text(
    request: TextGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate text using AI provider.

    This endpoint:
    1. Loads the specified prompt template
    2. Injects customer persona information (if selected in prompt)
    3. Loads the model configuration
    4. Decrypts API credentials
    5. Calls the AI provider
    6. Returns generated content

    Args:
        request: Text generation request (prompt_id, model_config_id, temperature, max_tokens)
        db: Database session
        current_user: Current authenticated user

    Returns:
        TextGenerationResponse: Generated text content with metadata

    Raises:
        HTTPException: If prompt, model config, or credentials not found/invalid
    """
    # Create generation service
    service = GenerationService(db)

    # Generate text
    try:
        response = await service.generate_text(
            user=current_user,
            prompt_id=request.prompt_id,
            model_config_id=request.model_config_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # If generation failed, raise HTTP exception
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error or "Text generation failed",
            )

        # Return successful response with prompt_id
        return TextGenerationResponse(
            content=response.content,
            model_used=response.model_used,
            provider=response.provider,
            prompt_id=request.prompt_id,
            usage=response.usage,
            success=True,
            error=None,
            request_id=response.request_id,
        )

    except ValueError as e:
        # Handle validation errors (prompt not found, model not found, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}",
        )


@router.post("/image", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate image using AI provider (DALL-E or Flux).

    This endpoint:
    1. Loads the specified model configuration
    2. Decrypts API credentials for the provider
    3. Calls the AI image provider
    4. Returns base64 encoded image data

    Args:
        request: Image generation request with prompt and parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        ImageGenerationResponse: Generated image(s) with metadata

    Raises:
        HTTPException: If model config or credentials not found/invalid
    """
    service = ImageGenerationService(db)

    try:
        response = await service.generate_image(
            user=current_user,
            prompt=request.prompt,
            model_config_id=request.model_config_id,
            size=request.size,
            quality=request.quality,
            style=request.style,
            n=request.n,
            width=request.width,
            height=request.height,
            steps=request.steps,
            guidance=request.guidance,
            reference_image_url=request.reference_image_url,
            reference_image_strength=request.reference_image_strength,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error or "Image generation failed",
            )

        # Convert provider response to API response format
        images = []
        if response.image_data:
            images.append(ImageData(
                base64_data=response.image_data,
                format="png",
                revised_prompt=response.raw_response.get("revised_prompt") if response.raw_response else None,
            ))

        return ImageGenerationResponse(
            images=images,
            model_used=response.model_used,
            provider=response.provider,
            request_id=response.request_id or "",
            raw_response=response.raw_response,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}",
        )


@router.post("/image/reference", response_model=ReferenceImageUploadResponse)
async def upload_reference_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a reference image for style-guided generation."""
    try:
        s3_service = get_s3_service()
        upload_result = await s3_service.upload_file(
            file=file,
            user_id=current_user.id,
            prefix="reference-images",
        )
        return ReferenceImageUploadResponse(**upload_result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload reference image: {str(e)}",
        )

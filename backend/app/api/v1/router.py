"""
API v1 router - aggregates all endpoint routers.
"""
from fastapi import APIRouter
from app.api.v1 import auth, prompts, credentials, customer_info, models, generate, posts, templates, ocr

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "api_version": "v1",
    }


# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(credentials.router, prefix="/credentials", tags=["Credentials"])
api_router.include_router(customer_info.router, prefix="/customer-info", tags=["Customer Info"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(generate.router, prefix="/generate", tags=["Generation"])
api_router.include_router(posts.router, prefix="/posts", tags=["Posts"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR"])

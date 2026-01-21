"""
Posts CRUD endpoints for social media content management.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database import get_db
from app.models.user import User
from app.models.post import PostStatus as ModelPostStatus
from app.schemas.post import (
    PostCreate, PostUpdate, Post as PostSchema, PostList,
    PostStatus, MediaUploadResponse
)
from app.services.post_service import PostService
from app.services.s3_service import get_s3_service
from app.services.csv_export_service import get_csv_export_service
from app.utils.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=PostList)
async def list_posts(
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of posts to return"),
    status: Optional[PostStatus] = Query(None, description="Filter by status"),
    is_archived: Optional[bool] = Query(None, description="Filter by archive status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    search: Optional[str] = Query(None, description="Search in content"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List posts with optional filtering and pagination.

    Args:
        skip: Number of posts to skip (pagination)
        limit: Maximum number of posts to return
        status: Optional status filter
        is_archived: Optional archive status filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        search: Optional content search query
        db: Database session
        current_user: Current authenticated user

    Returns:
        PostList: List of posts with pagination info
    """
    service = PostService(db)

    # Convert schema enum to model enum if provided
    model_status = ModelPostStatus(status.value) if status else None

    posts, total = await service.list_posts(
        user_id=current_user.id,
        status=model_status,
        is_archived=is_archived,
        date_from=date_from,
        date_to=date_to,
        search=search,
        skip=skip,
        limit=limit,
    )

    return PostList(
        posts=posts,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=PostSchema, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new post.

    Args:
        post_in: Post creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        PostSchema: Created post
    """
    service = PostService(db)
    post = await service.create_post(
        user_id=current_user.id,
        post_data=post_in,
    )
    return post


@router.get("/export/csv")
async def export_posts_csv(
    status: Optional[PostStatus] = Query(None, description="Filter by status"),
    is_archived: Optional[bool] = Query(None, description="Filter by archive status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Export posts to CSV file.

    Args:
        status: Optional status filter
        is_archived: Optional archive status filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        StreamingResponse: CSV file download
    """
    service = PostService(db)

    # Convert schema enum to model enum if provided
    model_status = ModelPostStatus(status.value) if status else None

    # Get all posts matching filters (no pagination for export)
    posts, _ = await service.list_posts(
        user_id=current_user.id,
        status=model_status,
        is_archived=is_archived,
        date_from=date_from,
        date_to=date_to,
        skip=0,
        limit=10000,  # Reasonable limit for CSV export
    )

    # Generate CSV
    csv_service = get_csv_export_service()
    csv_content = csv_service.export_posts(posts)

    # Create streaming response
    filename = f"posts_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


@router.get("/{post_id}", response_model=PostSchema)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific post by ID.

    Args:
        post_id: Post ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PostSchema: Post details

    Raises:
        HTTPException: If post not found
    """
    service = PostService(db)
    post = await service.get_post(current_user.id, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.put("/{post_id}", response_model=PostSchema)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a post.

    Args:
        post_id: Post ID
        post_in: Post update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        PostSchema: Updated post

    Raises:
        HTTPException: If post not found
    """
    service = PostService(db)
    post = await service.update_post(
        user_id=current_user.id,
        post_id=post_id,
        post_data=post_in,
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a post.

    Args:
        post_id: Post ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If post not found
    """
    service = PostService(db)
    deleted = await service.delete_post(current_user.id, post_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return None


@router.post("/{post_id}/media", response_model=MediaUploadResponse)
async def upload_media(
    post_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload media to S3 and attach to post.

    Args:
        post_id: Post ID
        file: File to upload
        db: Database session
        current_user: Current authenticated user

    Returns:
        MediaUploadResponse: Upload details

    Raises:
        HTTPException: If post not found or upload fails
    """
    # Verify post exists and belongs to user
    service = PostService(db)
    post = await service.get_post(current_user.id, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Upload to S3
    try:
        s3_service = get_s3_service()
        upload_result = await s3_service.upload_file(file, current_user.id)

        # Add media URL to post
        await service.add_media(
            user_id=current_user.id,
            post_id=post_id,
            media_url=upload_result["s3_url"],
        )

        return MediaUploadResponse(**upload_result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload media: {str(e)}",
        )


@router.delete("/{post_id}/media")
async def remove_media(
    post_id: int,
    media_url: str = Query(..., description="S3 URL to remove"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Remove media from post and optionally delete from S3.

    Args:
        post_id: Post ID
        media_url: S3 URL to remove
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If post not found
    """
    service = PostService(db)
    post = await service.remove_media(
        user_id=current_user.id,
        post_id=post_id,
        media_url=media_url,
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Optionally delete from S3
    try:
        s3_service = get_s3_service()
        s3_key = s3_service.extract_key_from_url(media_url)
        if s3_key:
            s3_service.delete_file(s3_key)
    except Exception:
        pass  # Non-critical - media removed from post even if S3 delete fails

    return {"message": "Media removed successfully"}


@router.post("/{post_id}/publish", response_model=PostSchema)
async def publish_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mark a post as published.

    Args:
        post_id: Post ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PostSchema: Updated post

    Raises:
        HTTPException: If post not found
    """
    service = PostService(db)
    post = await service.publish_post(current_user.id, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.post("/{post_id}/archive", response_model=PostSchema)
async def archive_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Archive a published post.

    Args:
        post_id: Post ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PostSchema: Updated post

    Raises:
        HTTPException: If post not found or not published
    """
    service = PostService(db)
    try:
        post = await service.archive_post(current_user.id, post_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.post("/{post_id}/restore", response_model=PostSchema)
async def restore_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Restore an archived post.

    Args:
        post_id: Post ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PostSchema: Updated post

    Raises:
        HTTPException: If post not found
    """
    service = PostService(db)
    post = await service.restore_post(current_user.id, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


class BulkArchiveRequest(BaseModel):
    """Request body for bulk archive/restore operations."""
    post_ids: List[int] = Field(..., min_length=1, description="List of post IDs")


@router.post("/bulk/archive")
async def bulk_archive_posts(
    request: BulkArchiveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Archive multiple posts.

    Args:
        request: Bulk archive request with post IDs
        db: Database session
        current_user: Current authenticated user

    Returns:
        Count of archived posts
    """
    service = PostService(db)
    count = await service.bulk_archive_posts(current_user.id, request.post_ids)
    return {"archived_count": count, "message": f"Successfully archived {count} posts"}


@router.post("/bulk/restore")
async def bulk_restore_posts(
    request: BulkArchiveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Restore multiple archived posts.

    Args:
        request: Bulk restore request with post IDs
        db: Database session
        current_user: Current authenticated user

    Returns:
        Count of restored posts
    """
    service = PostService(db)
    count = await service.bulk_restore_posts(current_user.id, request.post_ids)
    return {"restored_count": count, "message": f"Successfully restored {count} posts"}

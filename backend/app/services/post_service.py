"""
Post service for CRUD operations and business logic.
"""
import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate, PostUpdate

logger = logging.getLogger(__name__)


class PostService:
    """Service for managing posts."""

    def __init__(self, db: AsyncSession):
        """Initialize post service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_post(
        self,
        user_id: int,
        post_data: PostCreate,
    ) -> Post:
        """Create a new post.

        Args:
            user_id: User ID
            post_data: Post creation data

        Returns:
            Created Post
        """
        post = Post(
            content=post_data.content,
            status=PostStatus(post_data.status.value),
            scheduled_at=post_data.scheduled_at,
            prompt_id=post_data.prompt_id,
            media_urls=post_data.media_urls,
            user_id=user_id,
        )

        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)

        logger.info(f"Created post {post.id} for user {user_id}")
        return post

    async def get_post(
        self,
        user_id: int,
        post_id: int,
    ) -> Optional[Post]:
        """Get a post by ID.

        Args:
            user_id: User ID for authorization
            post_id: Post ID

        Returns:
            Post or None if not found
        """
        result = await self.db.execute(
            select(Post).filter(
                Post.id == post_id,
                Post.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        user_id: int,
        status: Optional[PostStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Post], int]:
        """List posts with filtering and pagination.

        Args:
            user_id: User ID
            status: Optional status filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            search: Optional content search
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (posts list, total count)
        """
        # Build query
        query = select(Post).filter(Post.user_id == user_id)

        # Apply filters
        if status:
            query = query.filter(Post.status == status)

        if date_from:
            query = query.filter(Post.created_at >= date_from)

        if date_to:
            query = query.filter(Post.created_at <= date_to)

        if search:
            query = query.filter(Post.content.ilike(f"%{search}%"))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and order
        query = query.order_by(Post.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        posts = result.scalars().all()

        return posts, total

    async def update_post(
        self,
        user_id: int,
        post_id: int,
        post_data: PostUpdate,
    ) -> Optional[Post]:
        """Update a post.

        Args:
            user_id: User ID for authorization
            post_id: Post ID
            post_data: Update data

        Returns:
            Updated Post or None if not found
        """
        post = await self.get_post(user_id, post_id)
        if not post:
            return None

        # Update fields
        update_data = post_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value:
                setattr(post, field, PostStatus(value.value))
            else:
                setattr(post, field, value)

        await self.db.commit()
        await self.db.refresh(post)

        logger.info(f"Updated post {post_id} for user {user_id}")
        return post

    async def delete_post(
        self,
        user_id: int,
        post_id: int,
    ) -> bool:
        """Delete a post.

        Args:
            user_id: User ID for authorization
            post_id: Post ID

        Returns:
            True if deleted, False if not found
        """
        post = await self.get_post(user_id, post_id)
        if not post:
            return False

        await self.db.delete(post)
        await self.db.commit()

        logger.info(f"Deleted post {post_id} for user {user_id}")
        return True

    async def add_media(
        self,
        user_id: int,
        post_id: int,
        media_url: str,
    ) -> Optional[Post]:
        """Add media URL to a post.

        Args:
            user_id: User ID for authorization
            post_id: Post ID
            media_url: S3 URL to add

        Returns:
            Updated Post or None if not found
        """
        post = await self.get_post(user_id, post_id)
        if not post:
            return None

        # Append to media_urls
        current_urls = post.media_urls or []
        if media_url not in current_urls:
            current_urls.append(media_url)
            post.media_urls = current_urls

            await self.db.commit()
            await self.db.refresh(post)

        return post

    async def remove_media(
        self,
        user_id: int,
        post_id: int,
        media_url: str,
    ) -> Optional[Post]:
        """Remove media URL from a post.

        Args:
            user_id: User ID for authorization
            post_id: Post ID
            media_url: S3 URL to remove

        Returns:
            Updated Post or None if not found
        """
        post = await self.get_post(user_id, post_id)
        if not post:
            return None

        # Remove from media_urls
        current_urls = post.media_urls or []
        if media_url in current_urls:
            current_urls.remove(media_url)
            post.media_urls = current_urls

            await self.db.commit()
            await self.db.refresh(post)

        return post

    async def publish_post(
        self,
        user_id: int,
        post_id: int,
    ) -> Optional[Post]:
        """Mark a post as published.

        Args:
            user_id: User ID for authorization
            post_id: Post ID

        Returns:
            Updated Post or None if not found
        """
        post = await self.get_post(user_id, post_id)
        if not post:
            return None

        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(post)

        logger.info(f"Published post {post_id} for user {user_id}")
        return post

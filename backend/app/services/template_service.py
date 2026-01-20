"""
Template service for CRUD operations and business logic.
"""
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.template import Template, TemplateCategory
from app.schemas.template import TemplateCreate, TemplateUpdate

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing templates."""

    def __init__(self, db: AsyncSession):
        """Initialize template service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_template(
        self,
        user_id: int,
        template_data: TemplateCreate,
    ) -> Template:
        """Create a new template.

        Args:
            user_id: User ID
            template_data: Template creation data

        Returns:
            Created Template
        """
        template = Template(
            name=template_data.name,
            category=TemplateCategory(template_data.category.value),
            tags=template_data.tags,
            content=template_data.content,
            user_id=user_id,
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        logger.info(f"Created template {template.id} for user {user_id}")
        return template

    async def get_template(
        self,
        user_id: int,
        template_id: int,
    ) -> Optional[Template]:
        """Get a template by ID.

        Args:
            user_id: User ID for authorization
            template_id: Template ID

        Returns:
            Template or None if not found
        """
        result = await self.db.execute(
            select(Template).filter(
                Template.id == template_id,
                Template.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        user_id: int,
        category: Optional[TemplateCategory] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Template], int]:
        """List templates with filtering and pagination.

        Args:
            user_id: User ID
            category: Optional category filter
            tag: Optional tag filter
            search: Optional name/content search
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (templates list, total count)
        """
        # Build query
        query = select(Template).filter(Template.user_id == user_id)

        # Apply filters
        if category:
            query = query.filter(Template.category == category)

        if search:
            query = query.filter(
                (Template.name.ilike(f"%{search}%")) |
                (Template.content.ilike(f"%{search}%"))
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and order
        query = query.order_by(Template.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        templates = result.scalars().all()

        # Filter by tag in Python (JSON field filtering)
        if tag:
            templates = [t for t in templates if tag in (t.tags or [])]
            total = len(templates)

        return templates, total

    async def update_template(
        self,
        user_id: int,
        template_id: int,
        template_data: TemplateUpdate,
    ) -> Optional[Template]:
        """Update a template.

        Args:
            user_id: User ID for authorization
            template_id: Template ID
            template_data: Update data

        Returns:
            Updated Template or None if not found
        """
        template = await self.get_template(user_id, template_id)
        if not template:
            return None

        # Update fields
        update_data = template_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "category" and value:
                setattr(template, field, TemplateCategory(value.value))
            else:
                setattr(template, field, value)

        await self.db.commit()
        await self.db.refresh(template)

        logger.info(f"Updated template {template_id} for user {user_id}")
        return template

    async def delete_template(
        self,
        user_id: int,
        template_id: int,
    ) -> bool:
        """Delete a template.

        Args:
            user_id: User ID for authorization
            template_id: Template ID

        Returns:
            True if deleted, False if not found
        """
        template = await self.get_template(user_id, template_id)
        if not template:
            return False

        await self.db.delete(template)
        await self.db.commit()

        logger.info(f"Deleted template {template_id} for user {user_id}")
        return True

    async def get_all_tags(
        self,
        user_id: int,
    ) -> List[str]:
        """Get all unique tags used in user's templates.

        Args:
            user_id: User ID

        Returns:
            List of unique tag strings
        """
        result = await self.db.execute(
            select(Template.tags).filter(Template.user_id == user_id)
        )
        all_tags = set()
        for row in result.scalars().all():
            if row:
                all_tags.update(row)
        return sorted(list(all_tags))

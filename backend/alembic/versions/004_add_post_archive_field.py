"""Add archive fields to posts table.

Revision ID: 004_add_post_archive_field
Revises: 003_add_templates_table
Create Date: 2025-01-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_post_archive_field'
down_revision: Union[str, None] = '003_add_templates_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add archive fields to posts table
    op.add_column('posts', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('posts', sa.Column('archived_at', sa.DateTime(), nullable=True))
    # Add index for efficient filtering by archive status
    op.create_index('ix_posts_is_archived', 'posts', ['is_archived'])


def downgrade() -> None:
    op.drop_index('ix_posts_is_archived', table_name='posts')
    op.drop_column('posts', 'archived_at')
    op.drop_column('posts', 'is_archived')

"""Add additional fields to posts and prompts tables.

Revision ID: 002_add_post_prompt_fields
Revises: 001_add_posts_table
Create Date: 2024-01-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_post_prompt_fields'
down_revision: Union[str, None] = '001_add_posts_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to posts table
    op.add_column('posts', sa.Column('caption', sa.Text(), nullable=True))
    op.add_column('posts', sa.Column('alt_text', sa.Text(), nullable=True))
    op.add_column('posts', sa.Column('graphic_type', sa.String(100), nullable=True))
    op.add_column('posts', sa.Column('original_prompt_name', sa.String(255), nullable=True))
    op.add_column('posts', sa.Column('source_url', sa.String(500), nullable=True))
    op.add_column('posts', sa.Column('keep', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('posts', sa.Column('for_deletion', sa.Boolean(), nullable=False, server_default='false'))

    # Add new column to prompts table
    op.add_column('prompts', sa.Column('example_image', sa.String(500), nullable=True))


def downgrade() -> None:
    # Remove columns from posts table
    op.drop_column('posts', 'for_deletion')
    op.drop_column('posts', 'keep')
    op.drop_column('posts', 'source_url')
    op.drop_column('posts', 'original_prompt_name')
    op.drop_column('posts', 'graphic_type')
    op.drop_column('posts', 'alt_text')
    op.drop_column('posts', 'caption')

    # Remove column from prompts table
    op.drop_column('prompts', 'example_image')

"""Add posts table

Revision ID: 001_add_posts
Revises:
Create Date: 2025-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_add_posts'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create posts table."""
    # Create enum type for post status (skip if already exists)
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'poststatus'"))
    if not result.fetchone():
        post_status = postgresql.ENUM('DRAFT', 'SCHEDULED', 'PUBLISHED', name='poststatus', create_type=False)
        post_status.create(conn, checkfirst=True)

    # Reference existing enum type
    post_status_enum = postgresql.ENUM('DRAFT', 'SCHEDULED', 'PUBLISHED', name='poststatus', create_type=False)

    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', post_status_enum, nullable=False, server_default='DRAFT', index=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('media_urls', sa.JSON(), nullable=False, default=[]),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('prompt_id', sa.Integer(), sa.ForeignKey('prompts.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(),
                  onupdate=sa.func.now()),
    )

    # Create indexes for common queries
    op.create_index('ix_posts_user_status', 'posts', ['user_id', 'status'])
    op.create_index('ix_posts_user_created', 'posts', ['user_id', 'created_at'])


def downgrade() -> None:
    """Drop posts table."""
    op.drop_index('ix_posts_user_created', table_name='posts')
    op.drop_index('ix_posts_user_status', table_name='posts')
    op.drop_table('posts')

    # Drop enum type
    post_status = postgresql.ENUM('DRAFT', 'SCHEDULED', 'PUBLISHED', name='poststatus')
    post_status.drop(op.get_bind(), checkfirst=True)

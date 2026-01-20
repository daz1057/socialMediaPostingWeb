"""Add templates table.

Revision ID: 003_add_templates_table
Revises: 002_add_post_prompt_fields
Create Date: 2024-01-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_templates_table'
down_revision: Union[str, None] = '002_add_post_prompt_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create templates table
    op.create_table(
        'templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('category', sa.Enum('ocr', 'manual', 'custom', name='templatecategory'), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False, default=[]),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_templates_id'), 'templates', ['id'], unique=False)
    op.create_index(op.f('ix_templates_name'), 'templates', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_templates_name'), table_name='templates')
    op.drop_index(op.f('ix_templates_id'), table_name='templates')
    op.drop_table('templates')
    # Drop the enum type
    op.execute('DROP TYPE IF EXISTS templatecategory')

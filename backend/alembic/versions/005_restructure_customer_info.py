"""Restructure customer_info table for category-based system

Revision ID: 005
Revises: 004_add_post_archive_field
Create Date: 2025-01-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_restructure_customer_info'
down_revision: Union[str, None] = '004_add_post_archive_field'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type for customer categories
    customercategory = postgresql.ENUM(
        'Pain',
        'Pleasures',
        'Desires',
        'Relatable Truths',
        'Customer Persona',
        'Artist Persona',
        'Brand',
        'In Groups and Out Groups',
        'Pun Primer',
        'USP',
        'Roles',
        name='customercategory',
        create_type=True
    )
    customercategory.create(op.get_bind(), checkfirst=True)

    # Drop old unique index if it exists
    op.drop_index('idx_user_customer_key', table_name='customer_info', if_exists=True)

    # Drop old columns if they exist
    # First check if key column exists and drop it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('customer_info')]

    if 'key' in columns:
        op.drop_column('customer_info', 'key')

    if 'content' in columns:
        op.drop_column('customer_info', 'content')

    # Add new columns
    if 'category' not in columns:
        op.add_column(
            'customer_info',
            sa.Column(
                'category',
                customercategory,
                nullable=True  # Temporarily allow null for existing rows
            )
        )

    if 'details' not in columns:
        op.add_column(
            'customer_info',
            sa.Column(
                'details',
                sa.JSON(),
                nullable=False,
                server_default='[]'
            )
        )

    # Create new unique index
    op.create_index(
        'idx_user_customer_category',
        'customer_info',
        ['user_id', 'category'],
        unique=True
    )

    # Create regular index on category
    op.create_index(
        'ix_customer_info_category',
        'customer_info',
        ['category']
    )


def downgrade() -> None:
    # Drop new indexes
    op.drop_index('idx_user_customer_category', table_name='customer_info', if_exists=True)
    op.drop_index('ix_customer_info_category', table_name='customer_info', if_exists=True)

    # Drop new columns
    op.drop_column('customer_info', 'category')
    op.drop_column('customer_info', 'details')

    # Add back old columns
    op.add_column(
        'customer_info',
        sa.Column('key', sa.String(100), nullable=False)
    )
    op.add_column(
        'customer_info',
        sa.Column('content', sa.JSON(), nullable=False)
    )

    # Recreate old index
    op.create_index(
        'idx_user_customer_key',
        'customer_info',
        ['user_id', 'key'],
        unique=True
    )

    # Drop the enum type
    customercategory = postgresql.ENUM(
        'Pain',
        'Pleasures',
        'Desires',
        'Relatable Truths',
        'Customer Persona',
        'Artist Persona',
        'Brand',
        'In Groups and Out Groups',
        'Pun Primer',
        'USP',
        'Roles',
        name='customercategory'
    )
    customercategory.drop(op.get_bind(), checkfirst=True)

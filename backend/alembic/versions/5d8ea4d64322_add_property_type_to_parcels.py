"""add_property_type_to_parcels

Revision ID: 5d8ea4d64322
Revises: 95e5d2bf2c4a
Create Date: 2026-07-08 21:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5d8ea4d64322'
down_revision: Union[str, Sequence[str], None] = '95e5d2bf2c4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('parcels', sa.Column('property_type', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('parcels', 'property_type')
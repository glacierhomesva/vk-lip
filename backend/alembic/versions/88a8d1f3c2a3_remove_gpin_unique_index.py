"""Remove unique constraint from gpin

Revision ID: 88a8d1f3c2a3
Revises: 73e36a59ac3c
Create Date: 2026-07-08 18:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88a8d1f3c2a3'
down_revision: Union[str, Sequence[str], None] = '73e36a59ac3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_parcels_gpin'), table_name='parcels')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_index(op.f('ix_parcels_gpin'), 'parcels', ['gpin'], unique=True)

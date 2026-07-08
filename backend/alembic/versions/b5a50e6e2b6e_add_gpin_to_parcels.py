"""Add gpin to parcels table

Revision ID: b5a50e6e2b6e
Revises: c0819cec8d89
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5a50e6e2b6e'
down_revision: Union[str, Sequence[str], None] = 'c0819cec8d89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'parcels',
        sa.Column('gpin', sa.String(length=50), nullable=True),
    )
    op.create_index(op.f('ix_parcels_gpin'), 'parcels', ['gpin'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_parcels_gpin'), table_name='parcels')
    op.drop_column('parcels', 'gpin')

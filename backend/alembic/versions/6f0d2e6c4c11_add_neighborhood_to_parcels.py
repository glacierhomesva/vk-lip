"""add_neighborhood_to_parcels

Revision ID: 6f0d2e6c4c11
Revises: 1324a548d82b
Create Date: 2026-07-08 20:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f0d2e6c4c11'
down_revision: Union[str, Sequence[str], None] = '1324a548d82b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('parcels', sa.Column('neighborhood', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_parcels_neighborhood'), 'parcels', ['neighborhood'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_parcels_neighborhood'), table_name='parcels')
    op.drop_column('parcels', 'neighborhood')

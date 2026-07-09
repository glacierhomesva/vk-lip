"""add_tax_delinquency_fields_to_parcels

Revision ID: 95e5d2bf2c4a
Revises: 6f0d2e6c4c11
Create Date: 2026-07-08 21:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '95e5d2bf2c4a'
down_revision: Union[str, Sequence[str], None] = '6f0d2e6c4c11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('parcels', sa.Column('tax_delinquent', sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column('parcels', sa.Column('tax_lien_amount', sa.Numeric(12, 2), nullable=True))


def downgrade() -> None:
    op.drop_column('parcels', 'tax_lien_amount')
    op.drop_column('parcels', 'tax_delinquent')
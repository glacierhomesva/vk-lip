"""add_tax_delinquency_remarks_to_parcels

Revision ID: c4f7f3b6c9d1
Revises: 5d8ea4d64322
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4f7f3b6c9d1'
down_revision: Union[str, Sequence[str], None] = '5d8ea4d64322'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('parcels', sa.Column('tax_delinquency_remarks', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('parcels', 'tax_delinquency_remarks')
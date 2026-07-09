"""add_advanced_opportunity_fields_to_parcels

Revision ID: 1324a548d82b
Revises: 35aca5809938
Create Date: 2026-07-08 20:28:02.096969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1324a548d82b'
down_revision: Union[str, Sequence[str], None] = '35aca5809938'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("parcels", sa.Column("years_owned", sa.Integer(), nullable=True))
    op.add_column("parcels", sa.Column("sia_flag", sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column("parcels", sa.Column("developer_owned", sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column("parcels", sa.Column("adjacent_developer_owned", sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("parcels", "adjacent_developer_owned")
    op.drop_column("parcels", "developer_owned")
    op.drop_column("parcels", "sia_flag")
    op.drop_column("parcels", "years_owned")

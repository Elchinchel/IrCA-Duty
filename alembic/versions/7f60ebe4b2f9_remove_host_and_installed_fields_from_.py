"""remove host and installed fields from user

Revision ID: 7f60ebe4b2f9
Revises: 1f9be3673cb8
Create Date: 2025-02-25 11:49:15.068388

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7f60ebe4b2f9'
down_revision: Union[str, None] = '1f9be3673cb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('user', 'installed')
    op.drop_column('user', 'host')


def downgrade() -> None:
    op.add_column('user', sa.Column('host', sa.VARCHAR(length=2048), nullable=False))
    op.add_column('user', sa.Column('installed', sa.BOOLEAN(), nullable=False))

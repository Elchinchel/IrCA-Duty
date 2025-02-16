"""add WebSession

Revision ID: 1f9be3673cb8
Revises: e24f844ebbd4
Create Date: 2025-02-16 14:33:04.385105

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1f9be3673cb8'
down_revision: Union[str, None] = 'e24f844ebbd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'web_session',
        sa.Column('token', sa.String(length=512), nullable=False),
        sa.Column('create_time', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('token'),
    )


def downgrade() -> None:
    op.drop_table('web_session')

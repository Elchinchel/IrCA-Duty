"""migrate from ICAD v1.3.2

Revision ID: e24f844ebbd4
Revises: 9265e93e2ee0
Create Date: 2025-02-15 16:26:50.034397

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e24f844ebbd4'
down_revision: Union[str, None] = '9265e93e2ee0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # TODO
    pass


def downgrade() -> None:
    pass

"""add CUSTOMNOCASE collation

Revision ID: 81205ea84e0f
Revises: 95a5dca036ce
Create Date: 2025-03-02 00:59:47.429775

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from duty.database.sqlite import NOCASE_COLLATION


# revision identifiers, used by Alembic.
revision: str = '81205ea84e0f'
down_revision: Union[str, None] = '95a5dca036ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('user_template', schema=None) as batch_op:
        batch_op.alter_column(
            'name',
            existing_type=sa.String(255),
            type_=sa.String(255, collation=NOCASE_COLLATION),
            existing_nullable=False
        )
    with op.batch_alter_table('user_anim_template', schema=None) as batch_op:
        batch_op.alter_column(
            'name',
            existing_type=sa.String(255),
            type_=sa.String(255, collation=NOCASE_COLLATION),
            existing_nullable=False
        )
    with op.batch_alter_table('user_voice_template', schema=None) as batch_op:
        batch_op.alter_column(
            'name',
            existing_type=sa.String(255),
            type_=sa.String(255, collation=NOCASE_COLLATION),
            existing_nullable=False
        )


def downgrade() -> None:
    pass

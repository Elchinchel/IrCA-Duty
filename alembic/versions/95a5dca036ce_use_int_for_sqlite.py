"""use Int for sqlite

Revision ID: 95a5dca036ce
Revises: 7f60ebe4b2f9
Create Date: 2025-02-26 16:01:58.610767

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '95a5dca036ce'
down_revision: Union[str, None] = '7f60ebe4b2f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('instance_info', schema=None) as batch_op:
        batch_op.alter_column(
            'id',
            existing_type=sa.BIGINT(),
            type_=sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'),
            existing_nullable=False,
            autoincrement=True,
        )
    with op.batch_alter_table('trusted_user', schema=None) as batch_op:
        batch_op.alter_column(
            'id',
            existing_type=sa.BIGINT(),
            type_=sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'),
            existing_nullable=False,
            autoincrement=True,
        )
    with op.batch_alter_table('user_anim_template', schema=None) as batch_op:
        batch_op.alter_column(
            'id',
            existing_type=sa.BIGINT(),
            type_=sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'),
            existing_nullable=False,
            autoincrement=True,
        )
    with op.batch_alter_table('user_template', schema=None) as batch_op:
        batch_op.alter_column(
            'id',
            existing_type=sa.BIGINT(),
            type_=sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'),
            existing_nullable=False,
            autoincrement=True,
        )
    with op.batch_alter_table('user_voice_template', schema=None) as batch_op:
        batch_op.alter_column(
            'id',
            existing_type=sa.BIGINT(),
            type_=sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'),
            existing_nullable=False,
            autoincrement=True,
        )


def downgrade() -> None:
    pass

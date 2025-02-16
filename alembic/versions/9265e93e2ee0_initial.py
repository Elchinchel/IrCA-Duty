"""initial

Revision ID: 9265e93e2ee0
Revises:
Create Date: 2025-02-15 16:26:39.727982

"""

from typing import Sequence, Union

import sqlalchemy as sa

import duty.database.base
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9265e93e2ee0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chat',
        sa.Column('iris_id', sa.String(), nullable=False),
        sa.Column('peer_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=512), nullable=True),
        sa.Column('installed', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('iris_id'),
    )
    op.create_table(
        'instance_info',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('host', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('installed', sa.Boolean(), nullable=False),
        sa.Column('owner_vk_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'user',
        sa.Column('vk_id', sa.BigInteger(), nullable=False),
        sa.Column('host', sa.String(length=2048), nullable=False),
        sa.Column('installed', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('vk_id'),
    )
    op.create_table(
        'user_anim_template',
        sa.Column('speed', sa.Float(), nullable=False),
        sa.Column('frames', duty.database.base.AsJson(), nullable=False),
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('vk_id', sa.BigInteger(), nullable=False),
        sa.Column('cat', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_user_anim_template', 'user_anim_template', ['vk_id', 'name'], unique=True
    )
    op.create_table(
        'user_secrets',
        sa.Column('vk_id', sa.BigInteger(), nullable=False),
        sa.Column('cb_secret', sa.String(length=1024), nullable=True),
        sa.Column('dc_secret', sa.String(length=1024), nullable=True),
        sa.Column('vk_me_token', sa.String(length=512), nullable=True),
        sa.Column('vk_main_token', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('vk_id'),
    )
    op.create_table(
        'user_template',
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('attachments', duty.database.base.AsJson(), nullable=False),
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('vk_id', sa.BigInteger(), nullable=False),
        sa.Column('cat', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_user_template', 'user_template', ['vk_id', 'name'], unique=True
    )
    op.create_table(
        'user_voice_template',
        sa.Column('attachment', sa.String(length=512), nullable=False),
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('vk_id', sa.BigInteger(), nullable=False),
        sa.Column('cat', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_user_voice_template',
        'user_voice_template',
        ['vk_id', 'name'],
        unique=True,
    )
    op.create_table(
        'trusted_user',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('trusted_by_vk_id', sa.BigInteger(), nullable=False),
        sa.Column('vk_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ['trusted_by_vk_id'],
            ['user.vk_id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('trusted_user')
    op.drop_index('ix_user_voice_template', table_name='user_voice_template')
    op.drop_table('user_voice_template')
    op.drop_index('ix_user_template', table_name='user_template')
    op.drop_table('user_template')
    op.drop_table('user_secrets')
    op.drop_index('ix_user_anim_template', table_name='user_anim_template')
    op.drop_table('user_anim_template')
    op.drop_table('user')
    op.drop_table('instance_info')
    op.drop_table('chat')

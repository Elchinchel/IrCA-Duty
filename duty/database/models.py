from datetime import datetime, timezone
from typing import List, Protocol

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Mapped, mapped_column, relationship

from duty.database.base import AsJson, Base
from duty.database.sqlite import NOCASE_COLLATION


MAX_NAME_LEN = 255

# SqlAlchemy SQLite backend support autoincrement only for Integer field
# though sqlite library save this field as 64-bit integer
IdInteger = BigInteger().with_variant(sqlite.INTEGER(), 'sqlite')
NameString = String(MAX_NAME_LEN, collation=NOCASE_COLLATION)


class InstanceInfo(Base):
    __tablename__ = 'instance_info'

    host: Mapped[str]
    version: Mapped[str]
    installed: Mapped[bool]
    owner_vk_id: Mapped[int]

    id: Mapped[int] = mapped_column(IdInteger, primary_key=True, default=None)


class User(Base):
    __tablename__ = 'user'

    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    trusted_users: Mapped[List['TrustedUser']] = relationship(
        cascade='save-update, delete, delete-orphan',
        lazy='select',
        default_factory=list
    )


class TrustedUser(Base):
    __tablename__ = 'trusted_user'

    trusted_by_vk_id: Mapped[int] = mapped_column(ForeignKey('user.vk_id'))
    vk_id: Mapped[int] = mapped_column(BigInteger)

    id: Mapped[int] = mapped_column(IdInteger, primary_key=True, default=None)


class UserSecrets(Base):
    __tablename__ = 'user_secrets'

    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    cb_secret: Mapped[str] = mapped_column(String(1024), nullable=True)
    "Key for authorizing requests to duty"
    dc_secret: Mapped[str] = mapped_column(String(1024), nullable=True)
    "Key for authorizing requests to datacenter"

    vk_me_token: Mapped[str] = mapped_column(String(512), nullable=True)
    vk_main_token: Mapped[str] = mapped_column(String(512), nullable=True)


class Chat(Base):
    __tablename__ = 'chat'

    iris_id: Mapped[str] = mapped_column(primary_key=True)
    peer_id: Mapped[int] = mapped_column(BigInteger)

    name: Mapped[str] = mapped_column(String(512), nullable=True)
    installed: Mapped[bool] = mapped_column(Boolean(), default=False)


class BaseUserTemplate(Protocol):
    id: Mapped[int]
    vk_id: Mapped[int]
    cat: Mapped[str]
    name: Mapped[str]


class UserTemplate(Base):
    __tablename__ = 'user_template'

    vk_id: Mapped[int] = mapped_column(BigInteger)
    cat: Mapped[str] = mapped_column(NameString)
    name: Mapped[str] = mapped_column(NameString)
    payload: Mapped[str] = mapped_column(Text)
    attachments: Mapped[List[str]] = mapped_column(AsJson)
    id: Mapped[int] = mapped_column(IdInteger, primary_key=True, init=False)

    __table_args__ = (
        Index('ix_user_template', 'vk_id', 'name', unique=True),
    )


class UserVoiceTemplate(Base):
    __tablename__ = 'user_voice_template'

    vk_id: Mapped[int] = mapped_column(BigInteger)
    cat: Mapped[str] = mapped_column(NameString)
    name: Mapped[str] = mapped_column(NameString)
    attachment: Mapped[str] = mapped_column(String(512))
    id: Mapped[int] = mapped_column(IdInteger, primary_key=True, init=False)

    __table_args__ = (
        Index('ix_user_voice_template', 'vk_id', 'name', unique=True),
    )


class UserAnimTemplate(Base):
    __tablename__ = 'user_anim_template'

    vk_id: Mapped[int] = mapped_column(BigInteger)
    cat: Mapped[str] = mapped_column(NameString)
    name: Mapped[str] = mapped_column(NameString)
    speed: Mapped[float] = mapped_column()
    frames: Mapped[List[str]] = mapped_column(AsJson)
    id: Mapped[int] = mapped_column(IdInteger, primary_key=True, init=False)

    __table_args__ = (
        Index('ix_user_anim_template', 'vk_id', 'name', unique=True),
    )


class WebSession(Base):
    __tablename__ = 'web_session'

    token: Mapped[str] = mapped_column(String(512), primary_key=True)
    create_time: Mapped[int] = mapped_column(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp())
    )

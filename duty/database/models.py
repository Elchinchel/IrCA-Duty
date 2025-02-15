from typing import List

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from duty.database.base import AsJson, Base


class InstanceInfo(Base):
    __tablename__ = 'instance_info'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    host: Mapped[str]
    version: Mapped[str]
    installed: Mapped[bool]
    owner_vk_id: Mapped[int]


class User(Base):
    __tablename__ = 'user'

    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    host: Mapped[str] = mapped_column(String(2040), default='')
    installed: Mapped[bool] = mapped_column(Boolean(), default=False)

    trusted_users: Mapped[List['TrustedUser']] = relationship(
        cascade='save-update, delete, delete-orphan',
        lazy='select',
        default_factory=list
    )


class TrustedUser(Base):
    __tablename__ = 'trusted_user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    trusted_by_vk_id: Mapped[int] = mapped_column(ForeignKey('user.vk_id'))
    vk_id: Mapped[int] = mapped_column(BigInteger)


class UserSecrets(Base):
    __tablename__ = 'user_secrets'

    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    cb_secret: Mapped[str] = mapped_column(String(1020), nullable=True)
    "Key for authorizing requests to duty"
    dc_secret: Mapped[str] = mapped_column(String(1020), nullable=True)
    "Key for authorizing requests to datacenter"

    vk_me_token: Mapped[str] = mapped_column(String(510), nullable=True)
    vk_main_token: Mapped[str] = mapped_column(String(510), nullable=True)


class Chat(Base):
    __tablename__ = 'chat'

    iris_id: Mapped[str] = mapped_column(primary_key=True)
    peer_id: Mapped[int] = mapped_column(BigInteger)

    name: Mapped[str] = mapped_column(String(510), nullable=True)
    installed: Mapped[bool] = mapped_column(Boolean(), default=False)


class BaseUserTemplate:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    vk_id: Mapped[int] = mapped_column(BigInteger)
    cat: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))  # XXX ограничить при сейве


class UserTemplate(BaseUserTemplate, Base):
    __tablename__ = 'user_template'

    payload: Mapped[str] = mapped_column(Text)
    attachments: Mapped[List[str]] = mapped_column(AsJson)

    __table_args__ = (
        Index('ix_user_template', 'vk_id', 'name', unique=True),
    )


class UserVoiceTemplate(BaseUserTemplate, Base):
    __tablename__ = 'user_voice_template'

    attachment: Mapped[str] = mapped_column(String(510))

    __table_args__ = (
        Index('ix_user_voice_template', 'vk_id', 'name', unique=True),
    )


class UserAnimTemplate(BaseUserTemplate, Base):
    __tablename__ = 'user_anim_template'

    speed: Mapped[float] = mapped_column()
    frames: Mapped[List[str]] = mapped_column(AsJson)

    __table_args__ = (
        Index('ix_user_anim_template', 'vk_id', 'name', unique=True),
    )

from typing import Type, Optional, Sequence

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from duty.database.models import (
    UserTemplate,
    UserAnimTemplate,
    UserVoiceTemplate,
)
from duty.database.repository.template.base import (
    Existence,
    TemplateType,
    BaseUserTemplateRepository,
)


class BaseSqlTemplateRepository(BaseUserTemplateRepository[TemplateType]):
    __template_type__: Type[TemplateType]

    def __init__(self, session: Session, vk_id: int) -> None:
        self.vk_id = vk_id
        self._session = session

    def get(self, name: str) -> Optional[TemplateType]:
        template_cls = self.__template_type__

        stmt = (
            select(template_cls)
            .where(template_cls.vk_id == self.vk_id)
            .where(template_cls.name == name)
        )

        return self._session.execute(stmt).scalar_one_or_none()

    def list(
            self,
            count: int,
            offset: int,
            category: 'str | None',
    ) -> Sequence[TemplateType]:
        template_cls = self.__template_type__

        stmt = (
            select(template_cls)
            .where(template_cls.vk_id == self.vk_id)
            .limit(count)
            .offset(offset)
        )
        if category:
            stmt = stmt.where(template_cls.cat == category)

        return self._session.execute(stmt).scalars().all()

    def save(self, data: TemplateType):
        template_cls = self.__template_type__

        exists_stmt = select(
            exists(template_cls.name)
            .where(template_cls.name == data.name)
        )
        name_exists = self._session.execute(exists_stmt).scalar_one()

        self._session.add(data)
        self._session.flush()

        return Existence.EXIST if name_exists else Existence.NOT_EXIST


class UserTemplateRepository(BaseSqlTemplateRepository[UserTemplate]):
    __template_type__ = UserTemplate


class UserVoiceTemplateRepository(BaseSqlTemplateRepository[UserVoiceTemplate]):
    __template_type__ = UserVoiceTemplate


class UserAnimTemplateRepository(BaseSqlTemplateRepository[UserAnimTemplate]):
    __template_type__ = UserAnimTemplate

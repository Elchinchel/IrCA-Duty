from sqlalchemy import select
from sqlalchemy.orm import Session

from duty.database.accessor.base import BaseAccessor
from duty.database.models import InstanceInfo


class SqlInstanceInfoAccessor(BaseAccessor[InstanceInfo]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def set(self, data: InstanceInfo):
        assert data.id == 1
        return super().set(data)

    def get(self) -> InstanceInfo:
        result = self._session.execute(
            select(InstanceInfo)
        ).scalar_one_or_none()

        if result is None:
            result = InstanceInfo(
                host='',
                version='',
                installed=False,
                owner_vk_id=0,
                id=1
            )
            self._session.add(result)
        return result
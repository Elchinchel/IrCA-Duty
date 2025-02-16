from sqlalchemy import select
from sqlalchemy.orm import Session

from duty.database.accessor.base import BaseAccessor
from duty.database.models import InstanceInfo


class SqlInstanceInfoAccessor(BaseAccessor[InstanceInfo]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get(self) -> InstanceInfo:
        result = self._session.execute(
            select(InstanceInfo).limit(1)
        ).scalar_one_or_none()

        if result is None:
            return InstanceInfo('', '', False, 0)
        return result
from sqlalchemy import select
from sqlalchemy.orm import Session

from duty.database.accessor.base import BaseAccessor
from duty.database.models import UserSecrets


class SqlUserSecretsAccessor(BaseAccessor[UserSecrets]):
    def __init__(self, session: Session, vk_id: int) -> None:
        self.vk_id = vk_id
        super().__init__(session)

    def get(self) -> UserSecrets:
        stmt = select(UserSecrets).where(UserSecrets.vk_id == self.vk_id)
        return self._session.execute(stmt).scalar_one()

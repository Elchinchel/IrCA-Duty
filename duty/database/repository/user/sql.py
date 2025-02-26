from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from duty.database.models import User
from duty.database.repository.user.base import BaseUserRepository


class SqlUserRepository(BaseUserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, vk_id: int) -> User | None:
        stmt = select(User).where(User.vk_id == vk_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def must_get(self, vk_id: int) -> User:
        stmt = select(User).where(User.vk_id == vk_id)
        return self._session.execute(stmt).scalar_one()

    def set(self, user: User):
        self._session.add(user)
        self._session.flush()

    def delete(self, vk_id: int):
        stmt = delete(User).where(User.vk_id == vk_id)
        return self._session.execute(stmt)



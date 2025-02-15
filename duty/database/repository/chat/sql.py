from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from duty.database.models import Chat
from duty.database.repository.chat.base import BaseChatRepository


class SqlChatRepository(BaseChatRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, iris_id: str) -> Chat | None:
        stmt = select(Chat).where(Chat.iris_id == iris_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def save(self, Chat: Chat):
        self._session.add(Chat)
        self._session.flush()

    def delete(self, iris_id: str):
        stmt = delete(Chat).where(Chat.iris_id == iris_id)
        return self._session.execute(stmt)



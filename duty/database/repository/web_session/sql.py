from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from duty.database.models import WebSession
from duty.database.repository.web_session.base import BaseWebSessionRepository


class SqlWebSessionRepository(BaseWebSessionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, token: str) -> WebSession | None:
        stmt = select(WebSession).where(WebSession.token == token)
        return self._session.execute(stmt).scalar_one_or_none()

    def save(self, web_session: WebSession):
        self._session.add(web_session)
        self._session.flush()

    def delete(self, token: str):
        stmt = delete(WebSession).where(WebSession.token == token)
        return self._session.execute(stmt)



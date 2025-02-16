from abc import ABC, abstractmethod
from typing import Optional

from duty.database.models import WebSession


class BaseWebSessionRepository(ABC):
    @abstractmethod
    def get(self, token: str) -> Optional[WebSession]:
        raise NotImplementedError

    @abstractmethod
    def save(self, web_session: WebSession):
        raise NotImplementedError

    @abstractmethod
    def delete(self, token: str):
        raise NotImplementedError

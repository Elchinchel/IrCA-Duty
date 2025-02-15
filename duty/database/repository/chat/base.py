from abc import ABC, abstractmethod
from typing import Optional

from duty.database.models import Chat


class BaseChatRepository(ABC):
    @abstractmethod
    def get(self, iris_id: str) -> Optional[Chat]:
        raise NotImplementedError

    @abstractmethod
    def save(self, chat: Chat):
        raise NotImplementedError

    @abstractmethod
    def delete(self, iris_id: str):
        raise NotImplementedError

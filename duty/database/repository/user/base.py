from abc import ABC, abstractmethod
from typing import Optional

from duty.database.models import User


class BaseUserRepository(ABC):
    @abstractmethod
    def get(self, vk_id: int) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def must_get(self, vk_id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    def set(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def delete(self, vk_id: int):
        raise NotImplementedError

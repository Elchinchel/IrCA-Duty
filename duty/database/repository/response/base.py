from abc import ABC, abstractmethod
from typing import Mapping


class BaseResponseRepository(ABC):
    @abstractmethod
    def must_get(self, key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> Mapping[str, str]:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: str):
        raise NotImplementedError

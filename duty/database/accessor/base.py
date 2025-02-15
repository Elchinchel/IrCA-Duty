from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session


ObjType = TypeVar('ObjType')


class BaseAccessor(ABC, Generic[ObjType]):
    def __init__(self, session: Session) -> None:
        self._session = session

    @abstractmethod
    def get(self) -> ObjType:
        raise NotImplementedError

    def set(self, data: ObjType):
        self._session.add(data)
        self._session.flush()

from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, Optional, Sequence, TypeVar

from duty.database.models import BaseUserTemplate


TemplateType = TypeVar('TemplateType', bound=BaseUserTemplate)


class Existence(Enum):
    EXIST = 'exist'
    NOT_EXIST = 'not_exist'


class BaseUserTemplateRepository(ABC, Generic[TemplateType]):
    @abstractmethod
    def get(self, name: str) -> Optional[TemplateType]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, ident: int) -> Optional[TemplateType]:
        raise NotImplementedError

    @abstractmethod
    def list(
            self,
            count: Optional[int],
            offset: Optional[int],
            category: Optional[str],
    ) -> Sequence[TemplateType]:
        raise NotImplementedError

    @abstractmethod
    def save(self, data: TemplateType) -> Existence:
        raise NotImplementedError

    @abstractmethod
    def delete(self, name: str) -> Existence:
        raise NotImplementedError

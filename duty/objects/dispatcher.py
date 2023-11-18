import traceback
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar, Callable, Iterable
from logging import getLogger

from typing_extensions import Self, TypeAlias

from duty.utils import UnrewritableMapping
from duty.vk.api import VkApiResponseException
from duty.dto.iris import IrisCBAPIErrorCode
from duty.objects.events import (
    BaseEvent,
    SignalEvent,
    LongpollEvent,
    MySignalEvent,
    MessageEventType
)
from duty.objects.exceptions import IrisCBAPIError


_KT = TypeVar('_KT')
_VT = TypeVar('_VT')
HandlerType: TypeAlias = 'Callable[[BaseEvent], dict[str, Any] | None]'

logger = getLogger(__name__)


def _make_registrator(
        target_map: Dict[_KT, _VT],
        registering_keys: 'Iterable[_KT]',
        map_name: str,
) -> Callable[[_VT], _VT]:
    def registrator(value):
        for key in registering_keys:
            if key in target_map:
                raise ValueError(f'{key!r} already registered ({target_map[key]!r})')
            logger.debug(f'{value!r} registered as {key!r} in {map_name}')
            target_map[key] = value
        return value

    return registrator


class BaseDispatcher(ABC):
    def _run_handler(
            self,
            event: BaseEvent,
            handler: HandlerType
    ):
        logger.info(f"Обработка {event!r}; F:{handler!r}")
        try:
            return handler(event)
        except VkApiResponseException as e:
            message = (f'Ошибка VK #{e.error_code}: {e.error_msg}\n'
                       f'{traceback.format_exc()}')
            logger.error(message)
            if e.error_code in {5, 6, 14, 924}:
                return {
                    "response": "vk_error",
                    "error_code": e.error_code,
                    "error_message": e.error_msg
                }
            return message
        except Exception:
            data = traceback.format_exc() + '\n\n' + str(event)
            logger.error(data)
            return data

    @abstractmethod
    def update(self, dp: Self):
        raise NotImplementedError

    def wrap_handler(self, wrapper):
        '''Заменяет передаваемый в декорируемую функцию аргумент на результат
        `wrapper(event)`''' # XXX
        def decorate(wrapped):
            def decorator(event: BaseEvent):
                wrap = wrapper(event)
                return wrapped(*wrap if type(wrap) == tuple else wrap)
            return decorator
        return decorate


class IrisCBAPIDispatcher(BaseDispatcher):
    _event_handlers: Dict[Type[BaseEvent], HandlerType]

    def __init__(self) -> None:
        self._event_handlers = {}

    def register(self, cls: 'type[BaseEvent]'):
        return _make_registrator(
            self._event_handlers,
            [cls],
            'iris_event_handlers'
        )

    def update(self, dp: Self):
        self._event_handlers.update(dp._event_handlers)

    def handle_event(self, event: BaseEvent):
        handler = self._event_handlers.get(event.msg.command)
        if handler is None:
            raise IrisCBAPIError(IrisCBAPIErrorCode.ERROR_NO_METHOD_FOUND)
        return self._run_handler(event, handler)


class SignalDispatcher(BaseDispatcher):
    __handlers_name__ = 'signal_handlers'

    _command_handlers: Dict[str, HandlerType]

    def __init__(self) -> None:
        self._command_handlers = {}

    def update(self, dp: Self):
        self._command_handlers.update(dp._command_handlers)

    def register(self, *commands: str):
        return _make_registrator(
            self._command_handlers,
            commands,
            self.__handlers_name__
        )

    def handle_event(self, event: MessageEventType):
        logger.info(f'Обрабатываю команду {event.msg.command}')

        handler = self._command_handlers.get(event.msg.command)
        if handler is None:
            raise IrisCBAPIError(IrisCBAPIErrorCode.ERROR_NO_METHOD_FOUND)
        return self._run_handler(event, handler)


class MySignalDispatcher(SignalDispatcher):
    __handlers_name__ = 'my_signal_handlers'


class LongpollSignalDispatcher(SignalDispatcher):
    __handlers_name__ = 'longpoll_signal_handlers'

from typing import TypeVar
from pathlib import Path
from functools import lru_cache
from importlib import import_module

from flask import current_app

from duty.objects.dispatcher import (
    BaseDispatcher,
    SignalDispatcher,
    IrisCBAPIDispatcher
)


DispatcherT = TypeVar('DispatcherT', bound=BaseDispatcher)


def _iter_dispatchers(cls: 'type[BaseDispatcher]'):
    root_dir = Path(__file__).parent

    for path in root_dir.glob('*/**/*.py'):
        import_path = list(path.relative_to(root_dir).parts)
        import_path[-1] = import_path[-1].rpartition('.py')[0]
        print(import_module('.' + '.'.join(import_path), 'duty.handlers'))
    return


@lru_cache
def _find_and_join_dispatchers(app, dispatcher_cls):
    dp = dispatcher_cls()
    for dispatcher in _iter_dispatchers(dispatcher_cls):
        dp.update(dispatcher)
    return dp


_find_and_join_dispatchers(None, IrisCBAPIDispatcher)


def find_and_join_dispatchers(dispatcher_cls: 'type[DispatcherT]') -> DispatcherT:
    return _find_and_join_dispatchers(
        current_app._get_current_object(),  # type: ignore
        dispatcher_cls
    )

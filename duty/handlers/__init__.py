from typing import TypeVar
from pathlib import Path
from logging import getLogger
from functools import lru_cache
from traceback import format_exc
from importlib import import_module

from flask import current_app

from duty.objects.dispatcher import (
    BaseDispatcher,
    SignalDispatcher,
    IrisCBAPIDispatcher
)


DispatcherT = TypeVar('DispatcherT', bound=BaseDispatcher)

logger = getLogger('handlers init')


def _iter_dispatchers(cls: 'type[BaseDispatcher]'):
    root_dir = Path(__file__).parent

    for path in root_dir.glob('*/**/*.py'):
        rel_path = path.relative_to(root_dir)
        import_path = list(rel_path.parts)
        import_path[-1] = import_path[-1].rpartition('.py')[0]
        try:
            module = import_module('.' + '.'.join(import_path), 'duty.handlers')
        except Exception:
            logger.critical('Failed to load %r:\n%s', rel_path, format_exc())
        else:
            print(module)
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

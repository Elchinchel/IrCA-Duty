import os
import random
from functools import lru_cache, partial
from inspect import Parameter, signature
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    ItemsView,
    Iterable,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)


dirname = os.path.dirname
joinpath = os.path.join

ROOT_DIR = Path(__file__).parent.parent.parent

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')


class UnrewritableMapping(Generic[_KT, _VT]):
    def __init__(self) -> None:
        self._map = {}

    def __contains__(self, __key: _KT) -> bool:
        return self._map.__contains__(__key)

    def __getitem__(self, __key: _KT) -> _VT:
        return self._map.__getitem__(__key)

    def __setitem__(self, __key: _KT, __value: _VT) -> None:
        if __key in self._map:
            raise KeyError(f'Key {__key!r} already present')
        return self._map.__setitem__(__key, __value)

    def get(self, __key: _KT) -> Union[_VT, None]:
        return self._map.get(__key)

    def update(self, __m: Iterable[Tuple[_KT, _VT]]) -> None:
        for key, value in __m:
            self.__setitem__(key, value)

    def items(self) -> ItemsView[_KT, _VT]:
        return self._map.items()


def gen_secret(
        chars: str = 'abcdefghijklmnopqrstuvwxyz0123456789',
        length: 'int | None' = None
):
    secret = ''
    length = length or random.randint(64, 80)
    while len(secret) < length:
        secret += chars[random.randint(0, len(chars)-1)]
    return secret


def get_index(item: Sequence, index: int, default: Any = None):
    try:
        return item[index]
    except IndexError:
        return default


def comma_separated_join(value: Iterable) -> str:
    return ','.join([str(i) for i in value])


@lru_cache(None)
def get_func_kwarg_names(func):
    sig = signature(func)
    kw_arg_names = []
    for param in sig.parameters.values():
        if param.kind == Parameter.KEYWORD_ONLY:
            kw_arg_names.append(param.name)
    return kw_arg_names


def fill_kw_only_params(func, data: Dict[str, Any]):
    """All keyword only parameters of func must be present in data"""
    return partial(
        func,
        **{name: data['name'] for name in get_func_kwarg_names(func)}
    )

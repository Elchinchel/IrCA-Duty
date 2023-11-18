import os
import re
import random
from typing import (
    Any,
    Dict,
    Tuple,
    Union,
    Generic,
    TypeVar,
    Iterable,
    Optional,
    Sequence,
    ItemsView
)
from pathlib import Path
from functools import wraps

from flask import g, request
from werkzeug.exceptions import BadRequest

from duty.vk import VkApi, VkApiResponseException


dirname = os.path.dirname
joinpath = os.path.join

DEV_ENV = (os.getenv('FLASK_ENV') == 'development')
ROOT_DIR = Path(__file__).parent.parent

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


def set_json_g_data(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        data = request.json
        if data is None:
            raise BadRequest('Failed to decode JSON object')
        g.data = data
        return func(*args, **kwargs)

    return decorator


def att_parse(attachments):
    atts = []
    if attachments:
        for i in attachments:
            att_t = i['type']
            if att_t in {'link', 'article'}: continue
            atts.append(att_t + str(i[att_t]['owner_id']) +
                        '_' + str(i[att_t]['id']))
            if i[att_t].get('access_key'):
                atts[-1] += '_' + i[att_t]['access_key']
    return atts


def format_response(text: str, **values):
    for key in values.keys():
        if not key.islower():
            values[key.lower()] = values.pop(key)
    for var_name in re.findall(r'{([^} ]+)}', text):
        if (lowcase := var_name.lower()) not in values:
            values[lowcase] = (
                f'[Ошибка! Не существует переменной "{var_name}", '
                 'ВНИМАТЕЛЬНО проверь название]'
            )
        text = text.replace('{'+var_name+'}', str(values[lowcase]))
    return text


def gen_secret(
        chars: str = 'abcdefghijklmnopqrstuvwxyz0123456789',
        length: 'int | None' = None
):
    secret = ''
    length = length or random.randint(64, 80)
    while len(secret) < length:
        secret += chars[random.randint(0, len(chars)-1)]
    return secret


def find_mention(text: str) -> Union[int, None]:
    for match in re.findall(r'\[(id|public|club)(\d*)\|', text):
        obj_id = int(match[1])
        if match[0] in ('club', 'public'):
            return 0 - obj_id
        return obj_id
    return None


def find_user_by_link(text: str, vk: VkApi) -> Union[int, None]:
    user = re.findall(r"vk.com\/(id\d*|[^ \n]*\b)", text)
    if user:
        try:
            return vk('users.get', user_ids=user)[0]['id']
        except (VkApiResponseException, IndexError):
            return None


def get_index(item: Sequence, index: int, default: Any = None):
    try:
        return item[index]
    except IndexError:
        return default


def format_push(u: dict) -> str:
    uid = u['id']
    if u.get('first_name') is None:
        return f"[club{abs(uid)}|{u['name']}]"
    else:
        return f"[id{uid}|{u['first_name']} {u['last_name']}]"


def get_plural(
        number: Union[int, float],
        one: str,
        few: str,
        many: Optional[str] = None,
        other: Optional[str] = None,
        suffix: str = ''
) -> str:
    """
    `one`  = 1, 21, 31, 41, 51, 61...\n
    `few`  = 2-4, 22-24, 32-34...\n
    `many` = 0, 5-20, 25-30, 35-40...\n
    `other` = 1.31, 2.31, 5.31...
    """
    assert isinstance(number, (int, float))

    if isinstance(number, float) and not number.is_integer():
        if other is None:
            other = few
        return other + suffix
    if many is None:
        many = few
    if (rem := number % 10) in {2, 3, 4} and not 10 < number % 100 < 20:
        return few + suffix
    elif rem == 1 and not 10 < number % 100 < 20:
        return one + suffix
    else:
        return many + suffix

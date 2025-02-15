import re
from typing import Union, Optional


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

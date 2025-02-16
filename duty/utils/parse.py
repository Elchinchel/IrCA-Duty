import re
from typing import Union

from flask import g, request
from werkzeug.exceptions import BadRequest

from duty.vk import VkApi, VkApiResponseException


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


class JsonParseMiddleware:
    def __init__(self, inner) -> None:
        self.inner = inner
        self.__name__ = inner.__name__

    def __call__(self, *args, **kwargs):
        data = request.json
        if data is None:  # XXX в каких случаях такое возможно?
            raise BadRequest('Failed to decode JSON object')
        g.data = data
        return self.inner(*args, **kwargs)


def set_json_g_data(func):
    return JsonParseMiddleware(func)

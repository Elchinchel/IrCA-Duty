import logging
from typing import Any

import requests


logger = logging.getLogger('VK API')


class VkApiResponseException(Exception):
    def __init__(self, data):
        self.error_code = data.get('error_code', None)
        self.error_msg = data.get('error_msg', None)
        self.request_params = data.get('request_params', None)

    def __str__(self):
        return 'Ошибка #%s: "%s"' % (self.error_code, self.error_msg)


class VkApi:
    url: str = 'https://api.vk.com/method/'
    query: str

    def __init__(self, access_token: str, version: str = "5.110"):
        self.query = f'?v={version}&access_token={access_token}&lang=ru'

    def __call__(self, method, **kwargs) -> Any:
        if logger.level < logging.INFO:
            logger.debug(f'URL = "{self.url}{method}{self.query}" Data = {kwargs}')

        r = requests.post(f'{self.url}{method}{self.query}', data=kwargs)
        if r.status_code == 200:
            r = r.json()
            if 'response' in r.keys():
                logger.info(f'Запрос {method} выполнен')
                return r['response']
            elif 'error' in r.keys():
                logger.warning(f"Запрос {method} не выполнен: {r['error']}")
                raise VkApiResponseException(**r["error"])
            return r
        else:
            raise Exception('networkerror', r.status_code)

    def send_msg(self, text: str, peer_id: int, **kwargs):
        return self.messages.send(
            message=text,
            peer_id=peer_id,
            random_id=0,
            **kwargs
        )

    def edit_msg(self, text: str, peer_id: int, message_id: int, **kwargs):
        return self.messages.edit(
            message=text,
            peer_id=peer_id,
            message_id=message_id,
            **kwargs
        )

    def delete_msg(self, message_id: int, for_all: bool):
        return self.messages.delete(
            message_id=message_id,
            delete_for_all=int(for_all)
        )

    def execute(self, code):
        return self('execute', code=code)

    def __getattr__(self, __name: str):
        return MethodGroup(self, __name)


class MethodGroup:
    def __init__(self, api: VkApi, name: str) -> None:
        self._api = api
        self._group = name

    def __getattr__(self, __name: str):
        def api_call(**kwargs):
            return self._api(f'{self._group}.{__name}', **kwargs)
        return api_call

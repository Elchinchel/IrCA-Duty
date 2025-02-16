import json
import logging
from typing import Any

import requests

from duty.vk.utils import VkSubject


logger = logging.getLogger('VK API')


class VkApiResponseException(Exception):
    def __init__(self, data):
        self.error_code = data.get('error_code', None)
        self.error_msg = data.get('error_msg', None)
        self.request_params = data.get('request_params', None)

    def __str__(self):
        return 'Ошибка #%s: "%s"' % (self.error_code, self.error_msg)


class UnknownResponse(Exception):
    ...


class VkApi:
    url: str = 'https://api.vk.com/method/'
    query: str

    def __init__(self, access_token: str, version: str = "5.130"):
        self.query = f'?v={version}&access_token={access_token}&lang=ru'
        self.subject = None

    def __call__(self, method, **kwargs) -> Any:
        if logger.level < logging.INFO:
            logger.debug(f'URL = "{self.url}{method}" Data = {kwargs}')

        resp = requests.post(f'{self.url}{method}{self.query}', data=kwargs)
        if resp.status_code == 200:
            resp = resp.json()

            if 'execute_errors' in resp:
                logger.warning(
                    'Ошибки при выполнении execute:\n%s',
                    json.dumps(resp['execute_errors'], ensure_ascii=False, indent=4)
                )

            if 'response' in resp.keys():
                logger.info('Запрос %r выполнен', method)
                return resp['response']

            if 'error' in resp.keys():
                logger.warning('Запрос %r не выполнен: %r', method, resp['error'])
                raise VkApiResponseException(resp['error'])

            raise UnknownResponse(resp)
        else:
            raise Exception('networkerror', resp.status_code)

    def get_subject(self) -> VkSubject:
        if self.subject is not None:
            return self.subject
        self.subject = VkSubject.fetch_self(self)
        return self.subject

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

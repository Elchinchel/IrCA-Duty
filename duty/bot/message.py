from html import unescape
from typing import List

from duty.vk import VkApi
from duty.vk.utils import VkMessage


class MessageRef:
    def __init__(self, message_id: int, peer_id: int, api: VkApi) -> None:
        self._id = message_id
        self._api = api
        self._peer = peer_id

    def edit(self, text: str, **params):
        self._api.edit_msg(text, self._peer, self._id)

    def delete(self, delete_for_all: bool = True):
        self._api.delete_msg(self._id, delete_for_all)


class Message(VkMessage):
    args: List[str]
    payload: str

    @property
    def command(self) -> str:
        if self._command is None:
            raise AttributeError('Message has no command')
        return self._command

    def __init__(self, msg: dict):
        msg['text'] = unescape(msg['text'])
        super().__init__(msg)
        self._parse_text()

    def _parse_text(self):
        args_str, _, payload = self.text.partition('\n')
        self.args = args_str.split()
        self.payload = payload

        if self.args:
            self._command = self.args.pop(0).lower()
        else:
            self._command = None

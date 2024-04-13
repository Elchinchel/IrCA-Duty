from html import unescape
from typing import List

from duty.utils import att_parse


class Message:
    _raw: dict

    id: int
    peer_id: int

    reply: dict
    fwd: List[dict]
    attachments: List[str]

    text: str
    args: List[str]
    payload: str

    def __init__(self, msg: dict):
        msg['text'] = unescape(msg['text'])

        self._raw = msg
        self._parse_text()

        self.fwd = msg.get('fwd_messages', [])
        self.reply = msg.get('reply_message', {})
        self.attachments = att_parse(msg.get('attachments', []))

    @property
    def command(self) -> str:
        if self._command is None:
            raise AttributeError('Message has no command')
        return self._command

    def _parse_text(self):
        args_str, _, payload = self.text.partition('\n')
        self.args = args_str.split()
        self.payload = payload

        if self.args:
            self._command = self.args.pop(0).lower()
        else:
            self._command = None

    def __getattr__(self, __name: str):
        try:
            return self._raw[__name]
        except KeyError:
            raise AttributeError(f'{type(self)!r} has no attribute {__name!r}') from None

from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Union

import requests


if TYPE_CHECKING:
    from duty.vk import VkApi
else:
    VkApi = ...


class ProxyObject:
    def __init__(self, obj: Dict[str, Any]) -> None:
        self._obj = obj

    def __repr__(self) -> str:
        cls = type(self).__name__
        return f'{cls}({self._obj})'

    def __getitem__(self, __name: str):
        return self._obj[__name]

    def __getattr__(self, __name: str):
        try:
            return self._obj[__name]
        except KeyError:
            pass
        return object.__getattribute__(self, __name)


class VkSubject(ProxyObject):
    """Wrap user or group object and provide access
    to their common fields
    """

    id: int

    @property
    def is_group(self) -> bool:
        return (self.id < 0)

    @property
    def name(self) -> str:
        if self.is_group:
            return self._obj['name']
        else:
            return f"{self.first_name} {self.last_name}"

    def push(self, name: 'str | None' = None):
        if name is None:
            name = self.name
        if self.is_group:
            return f'[club{self.id}|{name}]'
        else:
            return f'[id{self.id}|{name}]'

    @classmethod
    def fetch(cls, obj_id: int, api: VkApi):
        if obj_id > 0:
            data = api.users.get(user_ids=obj_id)[0]
        else:
            data = api.groups.getById(group_ids=obj_id)[0]
        return cls(data)

    @classmethod
    def fetch_self(cls, api: VkApi):
        code = 'return {"user": API.users.get(), "group": API.groups.getById()};'
        resp = api('execute', code=code)
        if resp['user']:
            return cls(resp['user'][0])
        if resp['group']:
            return cls(resp['group'][0])
        raise ValueError('Unexpected response: %r' % resp)


class VkMessage(ProxyObject):
    id: int
    peer_id: int
    from_id: int

    text: str

    @property
    def cmid(self) -> int:
        return self.conversation_message_id

    @cached_property
    def fwd(self) -> List[dict]:
        return self._obj.get('fwd_messages', [])

    @cached_property
    def reply(self) -> dict:
        return self._obj.get('reply_message', {})

    @cached_property
    def attachments(self) -> List[str]:
        return att_parse(self._obj.get('attachments', []))

    @classmethod
    def fetch_by_local_id(cls, api: VkApi, peer_id: int, local_id: int):
        resp = api.messages.getByConversationMessageId(
            conversation_message_ids=local_id, peer_id=peer_id
        )
        try:
            msg_obj = resp['items'][0]
        except (KeyError, IndexError):
            raise ValueError('Unknown message (id %d in peer %d)'
                             % (local_id, peer_id))
        return cls(msg_obj)


# XXX экспериментальненький интерфейс
class VkConversation:
    def __init__(self, peer_id: int) -> None:
        self.peer_id = peer_id

    def get_history(self) -> List[VkMessage]:
        return []


def att_parse(attachments):
    atts = []
    if attachments:
        for i in attachments:
            att_t = i['type']
            if att_t in ('link', 'article'):
                continue
            atts.append(att_t + str(i[att_t]['owner_id']) +
                        '_' + str(i[att_t]['id']))
            if i[att_t].get('access_key'):
                atts[-1] += '_' + i[att_t]['access_key']
    return atts


def get_last_th_msgs(peer_id: int, api: VkApi) -> List[dict]:
    return api.execute('''return (API.messages.getHistory({"peer_id":"%(peer)s",
    "count":"200", "offset":0}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":200}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":400}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":600}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":800}).items);''' % {'peer': peer_id})


def get_msgs(peer_id, api: VkApi, offset = 0):
    return api.execute('''return (API.messages.getHistory({"peer_id":"%s",
    "count":"200", "offset":"%s"}).items) + (API.messages.getHistory({"peer_id":
    "%s", "count":"200", "offset":"%s"}).items);''' %
    (peer_id, offset, peer_id, offset + 200))


def set_online_privacy(db, mode = 'only_me'):
    url = ('https://api.vk.com/method/account.setPrivacy?v=5.109&key=online&value=%s&access_token=%s'
    % (mode, db.me_token))
    r = requests.get(url, headers = {"user-agent": "VKAndroidApp/1.123-123 (Android 123; SDK 123; IrCA; 1; ru; 123x123)"}).json()
    if r['response']['category'] == mode:
        return True
    else:
        return False


def get_msg(vk: VkApi, peer_id: int, local_id: int) -> Union[dict, None]:
    try:
        return vk(
            "messages.getByConversationMessageId",
            conversation_message_ids=local_id, peer_id=peer_id
        )['items'][0]
    except (KeyError, IndexError):
        return None


def get_msg_id(vk: VkApi, peer_id: int, local_id: int) -> Union[int, None]:
    msg = get_msg(vk, peer_id, local_id)
    return msg['id'] if msg else None

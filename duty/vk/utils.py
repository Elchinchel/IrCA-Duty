from duty.vk import VkApi, VkApiResponseException
from typing import List,Union
import requests


class VkSubject:
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
            return self.data['name']
        else:
            return f"{self.first_name} {self.last_name}"

    def __init__(self, obj: dict) -> None:
        self.data = obj

    def __getattr__(self, __name: str):
        try:
            return self.data[__name]
        except KeyError:
            raise AttributeError from None

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
            data = api.users.get(user_ids=id)[0]
        else:
            data = api.groups.getById(group_ids=id)[0]
        return cls(data)


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

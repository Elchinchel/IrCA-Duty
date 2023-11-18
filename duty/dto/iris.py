from enum import Enum
from typing import Literal, TypedDict
from dataclasses import dataclass, field
from typing_extensions import NotRequired


class IrisCBAPIErrorCode(Enum):
    ERROR_NO_DATA = 1
    ERROR_NO_METHOD_FOUND = 2
    ERROR_USER_SECRET = 3
    ERROR_NO_CHAT = 4
    ERROR_CANT_BIND_CHAT = 10


class IrisCBAPIMethod(Enum):
    ADD_USER = 'addUser'
    BAN_EXPIRED = 'banExpired'
    BAN_GET_REASON = 'banGetReason'
    BIND_CHAT = 'bindChat'
    DELETE_MESSAGES_FROM_USER = 'deleteMessagesFromUser'
    DELETE_MESSAGES = 'deleteMessages'
    FORBIDDEN_LINKS = 'forbiddenLinks'
    PING = 'ping'
    PRINT_BOOKMARK = 'printBookmark'
    SUBSCRIBE_SIGNALS = 'subscribeSignals'
    TO_GROUP = 'toGroup'
    SEND_SIGNAL = 'sendSignal'
    SEND_MY_SIGNAL = 'sendMySignal'
    HIRE_API = 'hireApi'
    MEET_CHAT_DUTY = 'meetChatDuty'
    MESSAGES_DELETE_BY_TYPE = 'messages.deleteByType'
    GROUPBOTS_INVITED = 'groupbots.invited'
    MESSAGES_RECOGNISE_AUDIO_MESSAGE = 'messages.recogniseAudioMessage'


class IrisCBAPIErrorResponse(TypedDict):
    response: Literal['error', 'vk_error']
    error_code: int
    error_message: NotRequired[str]


@dataclass
class IrisCBAPIMessage:
    conversation_message_id: 'int | None'
    from_id: int
    date: int
    text: str


@dataclass
class AddUserObject:
    user_id: int
    chat: str
    source: 'str | None' = field(default=None)


@dataclass
class BanExpiredObject:
    user_id: int
    chat: str
    comment: str
    conversation_message_id: int


@dataclass
class BanGetReasonObject:
    chat: str
    local_id: int
    message: str


@dataclass
class BindChatObject:
    chat: str


@dataclass
class DeleteMessagesFromUserObject:
    chat: str
    member_ids: 'list[int]'
    amount: 'int | None' = field(default=None)
    silent: 'bool | None' = field(default=None)
    is_spam: 'bool | None' = field(default=None)


@dataclass
class DeleteMessagesObject:
    chat: str
    local_ids: 'list[int]'
    is_spam: bool
    silent: bool


@dataclass
class ForbiddenLinksObject:
    chat: str
    local_ids: 'list[int]'


@dataclass
class PrintBookmarkObject:
    chat: str
    conversation_message_id: int
    description: str


@dataclass
class SubscribeSignalsObject:
    chat: str
    conversation_message_id: int
    text: str
    from_id: int


@dataclass
class ToGroupObject:
    chat: str
    group_id: int
    local_id: int


@dataclass
class SendSignalObject:
    chat: str
    from_id: int
    value: str
    conversation_message_id: int


@dataclass
class SendMySignalObject:
    chat: str
    from_id: int
    value: str
    conversation_message_id: int


@dataclass
class HireApiObject:
    chat: str
    price: int


@dataclass
class MeetChatDutyObject:
    chat: str
    duty_id: int


@dataclass
class MessagesDeleteByTypeObject:
    chat: str
    type: Literal[
        'forwarded',
        'wall',
        'stickers',
        'voice',
        'gif',
        'photo',
        'video',
        'audio',
        'article',
        'period',
        'any'
    ]
    local_id: int
    offset: int
    is_spam: bool
    admin_ids: 'list[int]'
    time: int
    amount: int
    silent: 'bool | None' = field(default=None)


@dataclass
class GroupbotsInvitedObject:
    chat: str
    group_id: int


@dataclass
class MessagesRecogniseAudioMessageObject:
    chat: str
    local_id: int

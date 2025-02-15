from dataclasses import dataclass
from enum import Enum
from typing import Union


DC_HOST = 'https://api.lisi4ka.ru'
DC_GROUP_ID = -195759899


class ApiRequestPath:
    GET_STATS = f'{DC_HOST}/stat'
    CHECK_DC = f'{DC_HOST}/check'
    CHECK_USER = f'{DC_HOST}/reg/%d'
    REPEAT_MESSAGE = f'{DC_HOST}/repeat'


class DutyError(Enum):
    HOST_TROUBLES = 1
    NOT_TRUSTED = 2
    WRONG_SESSION = 3
    NOT_BINDED = 4
    VK_ERROR = 5


class DatacenterError(Enum):
    WRONG_SECRET = 'WrongSecret'
    WRONG_USER_ID = 'NotMe'


@dataclass
class DatacenterRequest:
    user_id: int
    secret: str


@dataclass
class DutyAuthorizedRequest:
    owner_id: int
    secret: str


# XXX: переделать дц а то порнография какая-то а не модели
@dataclass
class _RepeatMessageRequest:
    user_id: int
    chat: str
    local_id: int
    "conversation_message_id of target message"


@dataclass
class DutyRepeatMessageRequest(DutyAuthorizedRequest, _RepeatMessageRequest):
    pass


@dataclass
class DatacenterRepeatMessageRequest(DatacenterRequest, _RepeatMessageRequest):
    pass


@dataclass
class DatacenterSetSecretRequest(DatacenterRequest):
    secret: str


@dataclass
class DutyErrorResponse:
    error: Union[DutyError, DatacenterError]
    code: int = 0
    msg: str = ''


@dataclass
class DutyInfoResponse:
    v: str
    mt: bool
    me_id: int
    user_id: int
    owner_id: int

import json
import time

from typing import Dict, List, Union, get_type_hints
from logging import getLogger
from datetime import datetime

from flask import Request

from duty.vk import VkApi
from duty.utils import find_mention, find_user_by_link
from duty.vk.utils import get_msg
from duty.objects.chat import Chat, RawChat
from duty.objects.message import Message
from duty.objects.database import db
from duty.objects.exceptions import HandlingError, IrisCBAPIError
from duty.dto.iris import (
    DeleteMessagesFromUserObject,
    DeleteMessagesObject,
    ForbiddenLinksObject,
    GroupbotsInvitedObject,
    HireApiObject,
    IrisCBAPIMessage,
    IrisCBAPIMethod,
    AddUserObject,
    BanExpiredObject,
    BanGetReasonObject,
    BindChatObject,
    MeetChatDutyObject,
    MessagesDeleteByTypeObject,
    MessagesRecogniseAudioMessageObject,
    PrintBookmarkObject,
    SendMySignalObject,
    SendSignalObject,
    SubscribeSignalsObject,
    ToGroupObject,
    IrisCBAPIErrorCode
)


logger = getLogger('callback_events')


def load_iris_cb_api_event(data: dict) -> 'BaseEvent':
    if data['secret'] != db.secret or data['user_id'] != db.owner_id:
        raise IrisCBAPIError(IrisCBAPIErrorCode.ERROR_USER_SECRET)

    try:
        method = IrisCBAPIMethod(data['method'])
    except ValueError:
        raise IrisCBAPIError(IrisCBAPIErrorCode.ERROR_NO_METHOD_FOUND)

    cls = event_object_map[method]
    type_hints = get_type_hints(cls)
    obj_cls = type_hints['obj']
    should_parse_msg = (type_hints['msg'] is Message)
    should_bind_chat = (type_hints['chat'] is Chat)

    obj = obj_cls(**data['object'])
    api = VkApi(db.access_token, raise_excepts=True)

    try:
        msg = IrisCBAPIMessage(**data['message'])
    except KeyError:
        msg = None

    if should_bind_chat:
        chat = bind_chat(api, obj.chat_id, msg)
    else:
        chat = None

    if should_parse_msg:
        ERR_HEAD = 'Невозможно получить сообщение: '

        if chat is None:
            raise HandlingError(ERR_HEAD + 'в событии отсутствует чат')
        if msg is None:
            raise HandlingError(ERR_HEAD + 'в событии отсутствует объект сообщения')
        if msg.conversation_message_id is None:
            raise HandlingError(ERR_HEAD + 'в событии отсутствует идентификатор сообщения')

        raw_msg = get_msg(api, chat.peer_id, msg.conversation_message_id)
        if raw_msg is None:
            raise HandlingError(ERR_HEAD + f'VK не знает о сообщении {msg.conversation_message_id} в чате {chat.peer_id}')
        msg = Message(raw_msg)

    event = cls(api, obj, chat, msg)
    return event


def bind_chat(api: VkApi, chat_id: str, msg: 'IrisCBAPIMessage | None'):
    if chat_id in db.chats:
        return Chat(db.chats[chat_id], chat_id)

    if msg is None:
        raise IrisCBAPIError(IrisCBAPIErrorCode.ERROR_NO_CHAT)

    search_res = api.messages.search(q=msg.text, count=10, extended=1)
    event_message = _search_message(msg, search_res)
    chat_name = _search_conv_name(
        event_message['peer_id'], search_res['conversations']
    )

    db.chats[chat_id] = RawChat(
        peer_id=event_message['peer_id'],
        name=chat_name,
        installed=False
    )
    return Chat(db.chats[chat_id], chat_id)


def _search_message(target: IrisCBAPIMessage, messages):
    for msg in messages:
        if msg['conversation_message_id'] == target.conversation_message_id:
            if msg['from_id'] == target.from_id:  # XXX: message.date?
                return msg
    logger.error('Не удалось найти сообщение-команду для привязки чата')
    raise IrisCBAPIError(IrisCBAPIErrorCode.ERROR_CANT_BIND_CHAT)


def _search_conv_name(peer_id: int, conversations) -> str:
    for conv in conversations:
        if conv['peer']['id'] == peer_id:
            return conv['chat_settings']['title']
    raise HandlingError('VK проигнорировал просьбу прислать чаты с результатами поиска')


# if self.method in {'sendSignal', 'sendMySignal',
#                    'subscribeSignals', 'toGroup'}:
#     self.set_chat()
# elif self.method in {'ping', 'groupbots.invited',
#                      'bindChat', 'meetChatDuty'}:
#     pass
# else:
#     chat = self.obj['chat']
#     if chat not in self.db.chats:
#         raise ExceptToJson(f'Чат #{chat} не связан!')
#     self.chat = Chat(self.db.chats[chat], chat)


class BaseEvent:
    api: VkApi
    time: datetime

    def __init__(self, api, obj, chat, msg):
        self.api = api
        self.obj = obj
        self.msg = msg
        self.chat = chat
        self.time = datetime.now()

    def send(self, text='', **kwargs) -> int:
        if self.chat is None:
            raise RuntimeError('Чат неизвестен')
        return self.api.send_msg(text, self.chat.peer_id, **kwargs)

    def edit_msg(self, message_id: int, text='', **kwargs):
        if self.chat is None:
            raise RuntimeError('Чат неизвестен')
        return self.api.edit_msg(text, self.chat.peer_id, message_id, **kwargs)


class MessageEventType(BaseEvent):
    msg: Message


class SignalEvent(BaseEvent):
    msg: Message
    obj: SendSignalObject


class MyMessageMixin:
    api: VkApi
    msg: Message

    def send(self, message: str = '', **params) -> int:
        'Отправка в чат, из которого пришло событие, нового сообщения'
        return self.api.send_msg(message, self.msg.peer_id, **params)

    def edit(self, message: str = '', **params) -> int:
        'Редактирование сообщения-события'
        return self.api.edit_msg(message, self.msg.peer_id, self.msg.id, **params)

    def delete(self, for_all: bool = True) -> Dict[str, int]:
        'Удаление сообщения-события'
        return self.api.delete_msg(self.msg.id, for_all)

    def find_mention(self) -> Union[int, None]:
        'Возвращает ID пользователя, если он есть в сообщении, иначе None'
        user_id = find_mention(' '.join(self.msg.args))
        if not user_id and self.msg.reply_message:
            user_id = self.msg.reply_message['from_id']
        if not user_id:
            user_id = find_user_by_link(self.msg.text, self.api)
        if not user_id and self.msg.fwd:
            user_id = self.msg.fwd[0]['from_id']
        return user_id


class MySignalEvent(BaseEvent, MyMessageMixin):
    obj: SendMySignalObject


class LongpollEvent(BaseEvent, MyMessageMixin):
    data: dict

    def __str__(self) -> str:
        return f"""Новое событие от Longpoll модуля
            Команда: {self.command}
            Аргументы: {self.args}
            Данные: {self.data}
            Сообщение: {self.msg}
            """.replace("    ", "")

    def __init__(self, data: dict):
        self.time = datetime.now().timestamp()
        self.data = data
        self.msg = data['message']
        self.parse()
        self.command = data.get('command', self.command)
        if data['chat'] is None:
            self.chat = Chat({'peer_id': self.msg['peer_id']}, 'N/A')
        else:
            self.chat = Chat(self.db.chats[data['chat']], data['chat'])
        self.api = VkApi(self.db.access_token, raise_excepts=True)
        self.responses = self.db.responses

        logger.debug(self.__str__())


class AddUserEvent(BaseEvent):
    msg: None
    obj: AddUserObject


class BanExpiredEvent(BaseEvent):
    msg: None
    obj: BanExpiredObject


class BanGetReasonEvent(BaseEvent):
    msg: Message
    obj: BanGetReasonObject


class BindChatEvent(BaseEvent):
    msg: Message
    obj: BindChatObject


class DeleteMessagesFromUserEvent(BaseEvent):
    msg: Message
    obj: DeleteMessagesFromUserObject


class DeleteMessagesEvent(BaseEvent):
    msg: None
    obj: DeleteMessagesObject


class ForbiddenLinksEvent(BaseEvent):
    msg: None
    obj: ForbiddenLinksObject


class PingEvent(BaseEvent):
    msg: None
    obj: None
    chat: None


class PrintBookmarkEvent(BaseEvent):
    msg: Message
    obj: PrintBookmarkObject


class SubscribeSignalsEvent(BaseEvent):
    msg: Message
    obj: SubscribeSignalsObject


class ToGroupEvent(BaseEvent):
    msg: Message
    obj: ToGroupObject


class HireApiEvent(BaseEvent):
    msg: Message
    obj: HireApiObject


class MeetChatDutyEvent(BaseEvent):
    msg: None
    obj: MeetChatDutyObject


class MessagesDeleteByTypeEvent(BaseEvent):
    msg: None
    obj: MessagesDeleteByTypeObject


class GroupbotsInvitedEvent(BaseEvent):
    msg: None
    obj: GroupbotsInvitedObject


class MessagesRecogniseAudioMessageEvent(BaseEvent):
    msg: None
    obj: MessagesRecogniseAudioMessageObject


# 'dict[IrisCBAPIMethod, IrisCBAPIEvent]'
event_object_map = {
    IrisCBAPIMethod.ADD_USER: AddUserEvent,
    IrisCBAPIMethod.BAN_EXPIRED: BanExpiredEvent,
    IrisCBAPIMethod.BAN_GET_REASON: BanGetReasonEvent,
    IrisCBAPIMethod.BIND_CHAT: BindChatEvent,
    IrisCBAPIMethod.DELETE_MESSAGES_FROM_USER: DeleteMessagesFromUserEvent,
    IrisCBAPIMethod.DELETE_MESSAGES: DeleteMessagesEvent,
    IrisCBAPIMethod.FORBIDDEN_LINKS: ForbiddenLinksEvent,
    IrisCBAPIMethod.PING: PingEvent,
    IrisCBAPIMethod.PRINT_BOOKMARK: PrintBookmarkEvent,
    IrisCBAPIMethod.SUBSCRIBE_SIGNALS: SubscribeSignalsEvent,
    IrisCBAPIMethod.TO_GROUP: ToGroupEvent,
    IrisCBAPIMethod.SEND_SIGNAL: SignalEvent,
    IrisCBAPIMethod.SEND_MY_SIGNAL: MySignalEvent,
    IrisCBAPIMethod.HIRE_API: HireApiEvent,
    IrisCBAPIMethod.MEET_CHAT_DUTY: MeetChatDutyEvent,
    IrisCBAPIMethod.MESSAGES_DELETE_BY_TYPE: MessagesDeleteByTypeEvent,
    IrisCBAPIMethod.GROUPBOTS_INVITED: GroupbotsInvitedEvent,
    IrisCBAPIMethod.MESSAGES_RECOGNISE_AUDIO_MESSAGE: MessagesRecogniseAudioMessageEvent,
}

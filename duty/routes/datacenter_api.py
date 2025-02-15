from logging import FileHandler, getLogger
from pathlib import Path

from flask import g, jsonify, send_from_directory
from flask.blueprints import Blueprint
from werkzeug.exceptions import InternalServerError, ServiceUnavailable

from duty.bot.message import Message
from duty.database.accessor.base import BaseAccessor
from duty.database.models import Chat, InstanceInfo, UserSecrets
from duty.database.repository.chat.base import BaseChatRepository
from duty.database.repository.user.base import BaseUserRepository
from duty.dto.datacenter import (
    DC_GROUP_ID,
    DatacenterError,
    DatacenterRepeatMessageRequest,
    DatacenterRequest,
    DatacenterSetSecretRequest,
    DutyError,
    DutyInfoResponse,
)
from duty.utils.parse import set_json_g_data
from duty.vk import VkApi, VkApiResponseException
from library.adaptix import Retort
from library.dishka import Container, FromDishka
from library.dishka.integrations.flask import inject


bp = Blueprint('datacenter', __name__)
logger = getLogger(__name__)
retort = Retort()


def make_error_response(
        error_code: 'DutyError | DatacenterError',
        vk_error_code: int = 0,
        vk_error_message: str = ''
):
    data = {'error': error_code.value}
    if vk_error_code:
        data['code'] = vk_error_code
    if vk_error_message:
        data['msg'] = vk_error_message
    return jsonify(data)


def notify_datacenter(container: Container):
    inst_info = container.get(InstanceInfo)
    if not inst_info.installed:
        return

    secrets = container.get(UserSecrets)
    try:
        message = f'+cod {secrets.cb_secret} {inst_info.host}/'
        api = VkApi(secrets.vk_main_token)
        message_id = api.send_msg(message, DC_GROUP_ID)
        api.delete_msg(message_id, True)
    except Exception:  # noqa
        secrets.dc_secret = ''  # XXX: обновляются ли данные после коммита без вызова set? предположение: да, потому что объект после селекта привязан к активной сессии


class RequestValidateMiddleware:
    def __init__(self, inner, request_cls):
        self.inner = inner
        self.__name__ = inner.__name__

        self.request_cls = request_cls or DatacenterRequest
        self.pass_request = (request_cls is not None)

    @inject
    def __call__(
            self,
            inst_info: FromDishka[InstanceInfo],
            user_secrets_accessor: FromDishka[BaseAccessor[UserSecrets]]
    ):
        if not inst_info.installed:
            raise ServiceUnavailable('Duty not configured')

        request = retort.load(g.data, self.request_cls)

        if request.user_id != inst_info.owner_vk_id:
            return make_error_response(DatacenterError.WRONG_USER_ID)

        secrets = user_secrets_accessor.get()
        if request.secret != secrets.cb_secret:
            return make_error_response(DatacenterError.WRONG_SECRET)

        with g.dishka_container({UserSecrets: secrets}):
            if self.pass_request:
                return self.inner(request)
            return self.inner()


def ensure_request_valid(request_cls: 'type | None'):
    def decorator(func):
        handler = RequestValidateMiddleware(func, request_cls)
        return set_json_g_data(handler)
    return decorator


@bp.post('/dc')  # XXX: deprecated
@bp.post('/datacenter/secret')
@ensure_request_valid(DatacenterSetSecretRequest)
@inject
def set_dc_secret(
    request: DatacenterSetSecretRequest,
    user_secrets: FromDishka[UserSecrets]
):
    user_secrets.dc_secret = request.secret
    return 'ok'


@bp.post('/chex')  # XXX: deprecated
@bp.get('/datacenter/dutyInfo')
@ensure_request_valid(None)
@inject
def get_duty_info(
        user_secrets: FromDishka[UserSecrets],
        instance_info: FromDishka[InstanceInfo]
):
    def get_user_id_by_token(token: str):
        try:
            return VkApi(token, True)('users.get')[0]['id']
        except VkApiResponseException:
            return 0

    user_id = get_user_id_by_token(user_secrets.vk_main_token)
    user_me_id = get_user_id_by_token(user_secrets.vk_me_token)

    response = DutyInfoResponse(
        v=instance_info.version,
        mt=(user_me_id != 0),
        me_id=user_me_id,
        user_id=user_id,
        owner_id=instance_info.owner_vk_id,
    )
    return jsonify(retort.dump(response))


@bp.get('/log')  # XXX: deprecated
@bp.get('/datacenter/dutyLog')
@ensure_request_valid(None)
def get_duty_log():
    for handler in getLogger().handlers:
        if isinstance(handler, FileHandler):
            log_path = Path(handler.baseFilename)
            return send_from_directory(log_path.parent, log_path.name)
    raise InternalServerError('Logger has no file handlers')


@bp.post('/remote')  # XXX: deprecated
@bp.post('/datacenter/remoteMessage')
@ensure_request_valid(DatacenterRepeatMessageRequest)
@inject
def repeat_message(
        request: DatacenterRepeatMessageRequest,
        inst_info: FromDishka[InstanceInfo],
        user_secrets: FromDishka[UserSecrets],
        chat_repository: FromDishka[BaseChatRepository],
        user_repository: FromDishka[BaseUserRepository]
):
    user = user_repository.must_get(inst_info.owner_vk_id)

    for tr_user in user.trusted_users:
        if request.user_id == tr_user.vk_id:
            break
    else:
        return make_error_response(DutyError.NOT_TRUSTED)

    chat = chat_repository.get(request.chat)
    if chat is None:
        return make_error_response(DutyError.NOT_BINDED)

    try:
        return send_message_from_trusted_user(
            chat,
            request,
            user_secrets,
        )
    except VkApiResponseException as e:
        return make_error_response(
            DutyError.VK_ERROR,
            e.error_code,
            e.error_msg
        )
    except Exception:  # noqa
        logger.exception(
            "Ошибка при обработке запроса %s",
            request
        )
        return make_error_response(DutyError.HOST_TROUBLES)


def send_message_from_trusted_user(
        chat: Chat,
        request: DatacenterRepeatMessageRequest,
        user_secrets: UserSecrets,
):
    vk = VkApi(user_secrets.vk_main_token, raise_excepts=True)

    msg = vk.messages.getByConversationMessageId(
        peer_id=chat.peer_id,
        conversation_message_ids=request.local_id
    )['items'][0]

    if request.user_id != msg['from_id']:
        return make_error_response(DutyError.NOT_TRUSTED)

    msg = Message(msg)
    params = {'attachment': ','.join(msg.attachments)}
    if msg.reply:
        params['reply_to'] = msg.reply['id']
    elif msg.fwd:
        fwd_ids = ','.join([str(fwd['id']) for fwd in msg.fwd])
        params['forward_messages'] = fwd_ids

    vk.send_msg(msg.payload, chat.peer_id, **params)
    return 'ok'

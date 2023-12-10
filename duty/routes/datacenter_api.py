import json
import traceback

from enum import Enum
from pathlib import Path
from logging import getLogger, FileHandler
from functools import wraps

from flask import g, request, jsonify, send_from_directory
from flask.blueprints import Blueprint
from werkzeug.exceptions import BadRequest, InternalServerError

from duty.vk import VkApi, VkApiResponseException
from duty.utils import set_json_g_data
from duty.objects import Chat, Message, db, __version__


bp = Blueprint('datacenter', __name__)
logger = getLogger(__name__)


class DutyError(Enum):
    HOST_TROUBLES = 1
    NOT_TRUSTED = 2
    WRONG_SESSION = 3
    NOT_BINDED = 4
    VK_ERROR = 5


class DCError(Enum):
    WRONG_SECRET = 'WrongSecret'
    WRONG_USER_ID = 'NotMe'


def error(code: 'DutyError | DCError'):
    return jsonify({'error': code.value})


def ensure_request_valid(func):
    @wraps(func)
    @set_json_g_data
    def decorator(*args, **kwargs):
        if 'user_id' in g.data and g.data['user_id'] != db.owner_id:
            return error(DCError.WRONG_USER_ID)
        if g.data['secret'] != db.secret:
            return error(DCError.WRONG_SECRET)
        return func(*args, **kwargs)

    return decorator


@bp.record_once
def notify_datacenter(state):
    if db.installed:
        try:
            VkApi(db.access_token).execute('''API.messages.delete({
                "message_ids": API.messages.send({
                    "peer_id":-195759899, "message":"%s", "random_id": 0
                }),
                "delete_for_all": 1
            });''' % f'+cod {db.secret} {db.host}/')
        except Exception:
            db.dc_secret = None
            db.sync()


@bp.post('/dc')  # XXX: deprecated
@bp.post('/datacenter/secret')
@ensure_request_valid
def set_dc_secret():
    db.dc_secret = g.data['dc_secret']
    return 'ok'


@bp.post('/chex')  # XXX: deprecated
@bp.get('/datacenter/dutyInfo')
@ensure_request_valid
def get_duty_info():
    try:
        user_id = VkApi(db.access_token, True)('users.get')[0]['id']
    except VkApiResponseException:
        user_id = 0

    try:
        me_id = VkApi(db.me_token, True)('users.get')[0]['id']
    except VkApiResponseException:
        me_id = 0

    return jsonify({
        'owner_id': db.owner_id,
        'user_id': user_id,
        'me_id': me_id,
        'mt': (me_id != 0),
        'v': __version__
    })


@bp.get('/log')  # XXX: deprecated
@bp.get('/datacenter/dutyLog')
@ensure_request_valid
def get_duty_log():
    for handler in getLogger().handlers:
        if isinstance(handler, FileHandler):
            log_path = Path(handler.baseFilename)
            return send_from_directory(log_path.parent, log_path.name)
    raise InternalServerError('Logger has no file handlers')


@bp.post('/remote')  # XXX: deprecated
@bp.post('/datacenter/remoteMessage')
@ensure_request_valid
def send_remote_message():
    if g.data['user_id'] not in db.trusted_users:
        return error(DutyError.NOT_TRUSTED)
    if g.data['chat'] not in db.chats:
        return error(DutyError.NOT_BINDED)

    try:
        return send_message_from_trusted_user(g.data)
    except VkApiResponseException as e:
        return jsonify({
            'error': DutyError.VK_ERROR.value,
            'code': e.error_code,
            'msg': e.error_msg
        })
    except Exception:
        logger.error(
            "Ошибка при обработке запроса. Данные: %s\n%s",
            json.dumps(g.data, indent=2),
            traceback.format_exc()
        )
        return error(DutyError.HOST_TROUBLES)


def send_message_from_trusted_user(data: dict):
    vk = VkApi(db.access_token, raise_excepts=True)
    chat = Chat(db.chats[data['chat']], data['chat'])

    msg = vk.messages.getByConversationMessageId(
        peer_id=chat.peer_id,
        conversation_message_ids=data['local_id']
    )['items'][0]

    if data['user_id'] != msg['from_id']:
        return error(DutyError.NOT_TRUSTED)

    msg = Message(msg)
    params = {'attachment': ','.join(msg.attachments)}
    if msg.reply:
        params['reply_to'] = msg.reply['id']
    elif msg.fwd:
        fwd_ids = ','.join([str(fwd['id']) for fwd in msg.fwd])
        params['forward_messages'] = fwd_ids

    vk.send_msg(msg.payload, chat.peer_id, **params)
    return 'ok'

import json
import time
from functools import wraps

from flask import Blueprint, g, request
from logger import get_writer
from werkzeug.exceptions import BadRequest

from duty.vk import VkApi
from duty.utils import gen_secret, set_json_g_data
from duty.objects import LongpollEvent, db, dp


bp = Blueprint('longpoll_module', __name__)
logger = get_writer('Приемник сигналов LP модуля')


class error:
    AuthFail = 0


def ensure_request_authorized(func):
    @wraps(func)
    @set_json_g_data
    def decorator(*args, **kwargs):
        if g.data['access_key'] != db.lp_settings['key']:
            time.sleep(0.1)
            raise BadRequest('Invalid access key')
        return func(*args, **kwargs)

    return decorator


@bp.post('/ping')  # XXX: deprecated
@bp.get('/ping')
def ping():
    return "ok"


@bp.post('/longpoll/event')
@ensure_request_authorized
def longpoll():
    event = LongpollEvent(request.json)

    if event.data['access_key'] != event.db.lp_settings['key']:
        return "?"

    d = dp.longpoll_event_run(event)
    db.sync()
    if type(d) == dict:
        return json.dumps(d, ensure_ascii=False)
    return json.dumps({"response": "ok"}, ensure_ascii=False)


@bp.post('/longpoll/start')
@ensure_request_authorized
def get_data():
    token = json.loads(request.data)['token']

    try:
        if VkApi(token)('users.get')[0]['id'] != db.owner_id:
            raise ValueError
    except (KeyError, IndexError, ValueError):
        return json.dumps({'error': error.AuthFail})

    db.lp_settings['key'] = gen_secret(length=20)
    db.sync()
    return json.dumps({
        'chats': db.chats,
        'deleter': db.responses['del_self'],
        'settings': db.lp_settings,
        'self_id': db.owner_id
    })


@bp.route('/longpoll/sync', methods=["POST"])
@ensure_request_authorized
def sync_settings():
    db.lp_settings.update(g.data['settings'])
    return "ok"

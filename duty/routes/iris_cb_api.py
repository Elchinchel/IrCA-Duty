import json
from logging import getLogger

from flask import Response, Blueprint, g, request, current_app
from flask.blueprints import BlueprintSetupState
from werkzeug.exceptions import InternalServerError

from duty.vk import VkApiResponseException
from duty.utils import DEV_ENV, set_json_g_data
from duty.dto.iris import IrisCBAPIErrorCode
from duty.handlers import find_and_join_dispatchers
from duty.objects.events import load_iris_cb_api_event
from duty.objects.database import db
from duty.objects.dispatcher import IrisCBAPIDispatcher
from duty.objects.exceptions import HandlingError, IrisCBAPIError


bp = Blueprint('iris_callback', __name__)
logger = getLogger(__name__)


class ExceptToJson(Exception):
    response: str

    def __init__(self, message='', code: int = 0, iris: bool = False):
        if iris:
            self.response = json.dumps({
                    'response': 'error',
                    'error_code': code,
                    'error_message': message
                }, ensure_ascii=False)
        else:
            self.response = 'Error_o4ka:\n' + str(message)


@bp.post('/callback')
@set_json_g_data
def callback():
    dispatcher = find_and_join_dispatchers(IrisCBAPIDispatcher)
    if not DEV_ENV and g.data['secret'] != db.secret:
        raise IrisCBAPIError(IrisCBAPIErrorCode.ERROR_USER_SECRET)

    event = load_iris_cb_api_event(g.data)

    result = dispatcher.handle_event(event)
    return repr(result)

    if d is None:
        d = "ok"
    if d == "ok":
        return json.dumps({"response": "ok"}, ensure_ascii=False)
    elif type(d) == dict:
        return json.dumps(d, ensure_ascii=False)
    else:
        return r"\\\\\ашипка хэз бин произошла/////" + '\n' + d


@bp.errorhandler(ExceptToJson)
def json_error(e):
    return e.response


@bp.errorhandler(VkApiResponseException)
def vk_error(e: VkApiResponseException):
    return json.dumps({
        "response": "vk_error",
        "error_code": e.error_code,
        "error_message": e.error_msg
    }, ensure_ascii=False)

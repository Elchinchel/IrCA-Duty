from duty.utils import cmid_key
from duty.objects import dp, BaseEvent
from duty.objects.dispatcher import IrisCBAPIDispatcher
dp = IrisCBAPIDispatcher()
from duty.api_utils import get_msg_id


@dp.event_register('printBookmark')
def print_bookmark(event: BaseEvent) -> str:
    event.api.msg_op(1, event.chat.peer_id, event.obj['description'],
                     reply_to=get_msg_id(
                         event.api,
                         event.chat.peer_id,
                         event.obj[cmid_key]
                     ))
    return "ok"

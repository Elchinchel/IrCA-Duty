from idm.objects import dp, MySignalEvent
import time
import random

porn_list = ["doc-104156830_576067189", "doc389824243_575828415", "doc208945456_626479084"]

stickers = {
    "орех": 163,
    "агурец": 162, # я знаю, что это не "агурец", не ко мне вопросы
    "банан": 12669
}


@dp.my_signal_event_register(*stickers.keys())
def sticker(event: MySignalEvent) -> str:
    event.msg_op(3)
    event.msg_op(1, sticker_id=stickers.get(event.command))
    return "ok"


@dp.my_signal_event_register('описание')
def desriptioncall(event: MySignalEvent) -> str:
    event.msg_op(3)
    msg = event.msg_op(1, 'описание')
    time.sleep(3)
    event.api.msg_op(3, event.chat.peer_id, msg_id=msg)
    return "ok"


@dp.my_signal_event_register('auth')
def authmisc(event: MySignalEvent) -> str:
    event.msg_op(1, attachment='video155440394_168735361', reply_to=event.msg['id'])
    return "ok"

@dp.longpoll_event_register('гейпорно')
@dp.my_signal_event_register('гейпорно')
def gay_porn(event: MySignalEvent) -> str:
    event.msg_op(1, attachment=random.choice(porn_list), reply_to=event.msg['id'])
    return "ok"

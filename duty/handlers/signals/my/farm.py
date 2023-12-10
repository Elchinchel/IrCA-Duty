from duty.objects import dp, MySignalEvent
from duty.objects.dispatcher import MySignalDispatcher
dp = MySignalDispatcher()
from time import sleep


farm_data = {
    "owner_id": -174105461,
    "post_id": 6713149
}


@dp.longpoll_event_register('ферма')
@dp.my_signal_event_register('ферма')
def farming(event: MySignalEvent) -> str:
    comment_id = event.api('wall.createComment',
                           message='ферма', **farm_data)['comment_id']
    event.edit('⏱ Комментарий оставлен...')
    sleep(2)
    replies = event.api('wall.getComments',
                        **farm_data, comment_id=comment_id)['items']
    if replies:
        text = replies[0]['text'].rpartition('\n')
        event.edit(text[0] or text[2])
    else:
        event.edit('😐 Ирис не ответил.')
    return "ok"

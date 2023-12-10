from animstarter import start_player
from duty.objects import MySignalEvent, dp
from duty.objects.dispatcher import MySignalDispatcher
dp = MySignalDispatcher()
from .template import delete_template


@dp.longpoll_event_register('+анимка')
@dp.my_signal_event_register('+анимка')
def anim_create(event: MySignalEvent) -> str:
    name = ' '.join(event.args).lower()
    if not name:
        event.msg_op(2, "❗ Не указано название")
        return "ok"

    if not event.payload:
        event.msg_op(2, "❗ Нет данных")
        return "ok"

    event.db.anims, exist = delete_template(name, event.db.anims)
    event.db.anims.append({
        "speed": 1,
        "name": name,
        "frames": event.payload.split('#$')
    })

    event.msg_op(2, f'✅ Анимка "{name}" ' +
                 ('перезаписана' if exist else 'сохранена') +
                 '\n(лучше делать это в админ панели)')
    return "ok"


@dp.longpoll_event_register('анимки')
@dp.my_signal_event_register('анимки')
def anim_list(event: MySignalEvent) -> str:
    if event.db.anims:
        message = '📃 Список анимок:'
        for i, t in enumerate(event.db.anims, 1):
            message += f"\n{i}. {t['name']}"
    else:
        message = ('👀 Нет ни одной анимки... '
                   'Создать можно на сайте или командой +анимка')
    event.msg_op(2, message)
    return "ok"


@dp.longpoll_event_register('-анимка')
@dp.my_signal_event_register('-анимка')
def anim_delete(event: MySignalEvent) -> str:
    name = ' '.join(event.args).lower()
    if not name:
        event.msg_op(2, "❗ Не указано название")
        return "ok"
    event.db.anims, exist = delete_template(name, event.db.anims)
    if exist:
        msg = f'✅ Анимка "{name}" удалена'
    else:
        msg = f'⚠️ Анимка "{name}" не найдена'
    event.msg_op(2, msg, delete=2)
    return "ok"


@dp.longpoll_event_register('анимка')
@dp.my_signal_event_register('анимка')
def anim_play(event: MySignalEvent) -> str:
    name = ' '.join(event.args).lower()
    if not name:
        event.msg_op(2, "❗ Не указано название")
        return "ok"
    anim = None
    for a in event.db.anims:
        if a['name'].lower() == name:
            anim = a
            break
    if anim:
        start_player(event.chat.peer_id, event.msg['id'],
                     event.db.access_token,
                     anim['frames'], anim['speed'], True)
    else:
        event.msg_op(2, f'❗ Анимка "{name}" не найдена')
    return "ok"

from duty.objects import dp, MySignalEvent
from duty.utils import find_mention_by_event
from duty.vk import VkApiResponseException


@dp.longpoll_event_register('+др', '+друг', '-др', '-друг')
@dp.my_signal_event_register('+др', '+друг', '-др', '-друг')
def change_friend_status(event: MySignalEvent) -> str:
    user_id = find_mention_by_event(event)
    if user_id:
        if event.command.startswith('-др'):
            try:
                status = event.api('friends.delete', user_id=user_id)
                if status.get('friend_deleted'): msg = "💔 Пользователь удален из друзей"
                elif status.get('out_request_deleted'): msg = "✅ Отменена исходящая заявка"
                elif status.get('in_request_deleted'): msg = "✅ Отклонена входящая заявка"
                elif status.get('suggestion_deleted'): msg = "✅ Отклонена рекомендация друга"
                else: msg = "❗ Произошла ошибка"
            except VkApiResponseException as e:
                msg = f"❗ Произошла ошибка VK №{e.error_code} {e.error_msg}"
        else:
            try:
                status = event.api('friends.add', user_id = user_id)
                if status == 1: msg = "✅ Заявка отправлена"
                elif status == 2: msg = "✅ Пользователь добавлен"
                else: msg = "✅ Заявка отправлена повторно"
            except VkApiResponseException as e:
                if e.error_code == 174:
                    msg = "🤔 Ты себя добавить хочешь?"
                elif e.error_code == 175:
                    msg = "❗ Ты в ЧС данного пользователя"
                elif e.error_code == 176:
                    msg = "❗ Пользователь в ЧС"
                else:
                    msg = f"❗ Ошибка: {e.error_msg}"
    else:
        msg = "❗ Необходимо пересланное сообщение или упоминание"
    event.msg_op(2, msg)
    return "ok"


@dp.longpoll_event_register('+чс', '-чс')
@dp.my_signal_event_register('+чс', '-чс')
def ban_user(event: MySignalEvent) -> str:
    user_id = find_mention_by_event(event)
    if user_id:
        if event.command == '+чс':
            try:
                if event.api('account.ban', owner_id=user_id) == 1:
                    msg = '😡 Забанено'
            except VkApiResponseException as e:
                if e.error_msg.endswith('already blacklisted'):
                    msg = '❗ Пользователь уже забанен'
                else:
                    msg = f'❗ Ошиб_очка: {e.error_msg}'
        else:
            try:
                if event.api('account.unban', owner_id = user_id) == 1:
                    msg = '💚 Разбанено'
            except VkApiResponseException as e:
                if e.error_msg.endswith('not blacklisted'):
                    msg = '👌🏻 Пользователь не забанен'
                else:
                    msg = f'❗ Ошиб_очка: {e.error_msg}'
    else:
        msg = "❗ Необходимо пересланное сообщение или упоминание"
    event.msg_op(2, msg)
    return "ok"
from duty.vk import VkApiResponseException
from duty.vk.utils import VkSubject
from duty.utils import format_response
from duty.objects import BaseEvent
from duty.objects.events import BanExpiredEvent, AddUserEvent
from duty.objects.dispatcher import IrisCBAPIDispatcher
from duty.objects import db

dp = IrisCBAPIDispatcher()


def user_add(event: 'AddUserEvent | BanExpiredEvent', typ: str):
    user = VkSubject.fetch(event.obj.user_id, event.api)

    def _format(response_name, err=None):
        return format_response(
            db.responses[response_name],
            ссылка=user.push(), имя=event.chat.name, ошибка=err
        )

    if event.obj.user_id == db.owner_id:
        event.send(_format('user_ret_self'))

        return 'ok'

    message_id = event.send(_format(typ))

    try:
        event.api('messages.removeChatUser',
                  chat_id=event.chat.id, user_id=user['id'])
    except VkApiResponseException:
        pass

    try:
        event.api('messages.addChatUser',
                  chat_id=event.chat.id, user_id=user['id'])
        event.edit_msg(message_id, _format('user_ret_success'))
        return "ok"
    except VkApiResponseException as e:
        if e.error_code == 15:
            event.edit_msg(message_id, _format('user_ret_err_no_access'))
        else:
            event.edit_msg(message_id, _format('user_ret_err_vk', e.error_msg))
        return {
            "response":"vk_error",
            "error_code": e.error_code,
            "error_message": e.error_msg
        }
    except Exception:
        event.edit_msg(message_id, _format('user_ret_err_unknown'))
        return {"response":"error","error_code":"0","error_message":""}


@dp.event_register(AddUserEvent)
def add_user(event: BaseEvent) -> str:
    return user_add(event, 'user_ret_process')


@dp.register(BanExpiredEvent)
def ban_expired(event: BaseEvent) -> str:
    return user_add(event, 'user_ret_ban_expired')

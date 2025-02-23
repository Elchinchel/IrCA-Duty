import re
from enum import Enum
from typing import Any

from duty.database.repository.response.base import BaseResponseRepository


class RKey(Enum):
    DEL_SELF = 'del_self'
    DEL_PROCESS = 'del_process'
    DEL_SUCCESS = 'del_success'
    DEL_ERR_924 = 'del_err_924'
    DEL_ERR_VK = 'del_err_vk'
    DEL_ERR_NOT_FOUND = 'del_err_not_found'
    DEL_ERR_UNKNOWN = 'del_err_unknown'
    CHAT_SUBSCRIBE = 'chat_subscribe'
    CHAT_BIND = 'chat_bind'
    USER_RET_BAN_EXPIRED = 'user_ret_ban_expired'
    USER_RET_PROCESS = 'user_ret_process'
    USER_RET_SUCCESS = 'user_ret_success'
    USER_RET_ERR_NO_ACCESS = 'user_ret_err_no_access'
    USER_RET_ERR_VK = 'user_ret_err_vk'
    USER_RET_ERR_UNKNOWN = 'user_ret_err_unknown'
    USER_RET_SELF = 'user_ret_self'
    TO_GROUP_SUCCESS = 'to_group_success'
    TO_GROUP_ERR_FORBIDDEN = 'to_group_err_forbidden'
    TO_GROUP_ERR_RECS = 'to_group_err_recs'
    TO_GROUP_ERR_LINK = 'to_group_err_link'
    TO_GROUP_ERR_VK = 'to_group_err_vk'
    TO_GROUP_ERR_UNKNOWN = 'to_group_err_unknown'
    REPEAT_FORBIDDEN_WORDS = 'repeat_forbidden_words'
    REPEAT_IF_FORBIDDEN = 'repeat_if_forbidden'
    PING_DUTY = 'ping_duty'
    PING_MYSELF = 'ping_myself'
    PING_LP = 'ping_lp'
    INFO_DUTY = 'info_duty'
    INFO_MYSELF = 'info_myself'
    NOT_IN_TRUSTED = 'not_in_trusted'
    TRUSTED_ERR_NO_REPLY = 'trusted_err_no_reply'
    TRUSTED_ERR_IN_TR = 'trusted_err_in_tr'
    TRUSTED_ERR_NOT_IN_TR = 'trusted_err_not_in_tr'
    TRUSTED_SUCCESS_ADD = 'trusted_success_add'
    TRUSTED_SUCCESS_REM = 'trusted_success_rem'
    TRUSTED_LIST = 'trusted_list'


DEFAULT_RESPONSES = {
    RKey.DEL_SELF: "&#13;",
    RKey.DEL_PROCESS: "УДАЛЯЮ ЩАЩАЩ ПАДАЖЖЫ",
    RKey.DEL_SUCCESS: "✅ *Произошло удаление*",
    RKey.DEL_ERR_924: "❗ Не прокатило. Дежурный администратор? 🤔",
    RKey.DEL_ERR_VK: "❗ Не прокатило. Ошибка VK:{ошибка}",
    RKey.DEL_ERR_NOT_FOUND: "❗ Не нашел сообщения для удаления 🤷‍♀",
    RKey.DEL_ERR_UNKNOWN: "❗ Неизвестная ошибка при удалении 👀",
    RKey.CHAT_SUBSCRIBE: "РАБОТАЕТ 👍<br>Идентификатор чатика<br>{имя}<br>во вселенной ириса: {ид}",
    RKey.CHAT_BIND: "Чат '{имя}' успешно привязан!",
    RKey.USER_RET_BAN_EXPIRED: "💚 Срок бана пользователя {ссылка} истек",
    RKey.USER_RET_PROCESS: "💚 Добавляю {ссылка}",
    RKey.USER_RET_SUCCESS: "✅ Пользователь {ссылка} добавлен в беседу",
    RKey.USER_RET_ERR_NO_ACCESS: "❗ Не удалось добавить {ссылка}.<br>Нет доступа.<br> Возможно, он не в моих друзьях или он уже в беседе",
    RKey.USER_RET_ERR_VK: "❗ Не удалось добавить пользователя {ссылка}.<br>Ошибка ВК.<br>",
    RKey.USER_RET_ERR_UNKNOWN: "❗ Не удалось добавить пользователя {ссылка}.<br>Произошла неизвестная ошибка",
    RKey.USER_RET_SELF: "❗ Я уже тут.",
    RKey.TO_GROUP_SUCCESS: "✅ Запись опубликована",
    RKey.TO_GROUP_ERR_FORBIDDEN: "❗ Ошибка при публикации. Публикация запрещена. Превышен лимит на число публикаций в сутки, либо на указанное время уже запланирована другая запись, либо для текущего пользователя недоступно размещение записи на этой стене",
    RKey.TO_GROUP_ERR_RECS: "❗ Ошибка при публикации. Слишком много получателей",
    RKey.TO_GROUP_ERR_LINK: "❗ Ошибка при публикации. Запрещено размещать ссылки",
    RKey.TO_GROUP_ERR_VK: "❗ Ошибка при публикации. Ошибка VK:<br>{ошибка}",
    RKey.TO_GROUP_ERR_UNKNOWN: "❗ Ошибка при публикации. Неизвестная ошибка",
    RKey.REPEAT_FORBIDDEN_WORDS: [  # XXX оно не здесь быть должно
        "передать",
        "купить",
        "повысить",
        "завещание",
        "модер"
    ],
    RKey.REPEAT_IF_FORBIDDEN: "Я это писать не буду.",
    RKey.PING_DUTY: "{ответ}<br>Ответ за {время}сек.",
    RKey.PING_MYSELF: "{ответ} CB<br>Получено через {время}сек.<br>ВК ответил за {пингвк}сек.<br>Обработано за {обработано}сек.",
    RKey.PING_LP: "{ответ} LP<br>Получено через {время}сек.<br>Обработано за {обработано}сек.",
    RKey.INFO_DUTY: "Информация о дежурном:<br>IrCA Duty v{версия}<br>Владелец: {владелец}<br>Чатов: {чаты}<br><br>Информация о чате:<br>Iris ID: {ид}<br>Имя: {имя}",
    RKey.INFO_MYSELF: "Информация о дежурном:<br>IrCA Duty v{версия}<br>Владелец: {владелец}<br>Чатов: {чаты}<br><br>Информация о чате:<br>Iris ID: {ид}<br>Имя: {имя}",
    RKey.NOT_IN_TRUSTED: "Я тебе не доверяю 😑",
    RKey.TRUSTED_ERR_NO_REPLY: "❗ Ошибка при выполнении, необходимо пересланное сообщение",
    RKey.TRUSTED_ERR_IN_TR: "⚠ Пользователь уже в доверенных",
    RKey.TRUSTED_ERR_NOT_IN_TR: "⚠ Пользователь не находился в доверенных",
    RKey.TRUSTED_SUCCESS_ADD: "✅ Пользователь {ссылка} в доверенных",
    RKey.TRUSTED_SUCCESS_REM: "✅ Пользователь {ссылка} удален из доверенных",
    RKey.TRUSTED_LIST: "Доверенные пользователи:",
}

default_responses_str = {k.value: v for k, v in DEFAULT_RESPONSES.items()}


def format_response(text: str, values: 'dict[str, Any]'):
    for key in values.keys():
        if not key.islower():
            values[key.lower()] = values.pop(key)
    for var_name in re.findall(r'{([^}]+?)}', text):
        var_name = var_name.lower().strip()
        if (lowcase := var_name.lower()) not in values:
            values[lowcase] = (
                f'[Ошибка! Не существует переменной "{var_name}", '
                 'ВНИМАТЕЛЬНО проверь название]'
            )
        text = text.replace('{'+var_name+'}', str(values[lowcase]))
    return text


class ResponseMaker:
    def __init__(self, repo: BaseResponseRepository) -> None:
        self.repo = repo

    def format(self, key: RKey, **values):
        text = self.repo.must_get(key.value)
        return format_response(text, values)

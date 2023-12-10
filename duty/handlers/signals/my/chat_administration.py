import requests, io
from duty.utils import get_index, find_mention_by_event
from duty.objects import dp, MySignalEvent
from duty.objects.dispatcher import MySignalDispatcher
dp = MySignalDispatcher()
from duty.vk import VkApiResponseException

# code from:
# vk: http://vk.com/id194861150
# github: https://github.com/Alex1249

@dp.longpoll_event_register('добавить')
@dp.my_signal_event_register('добавить')
def add_user_in_chat(event: MySignalEvent):
    uid=find_mention_by_event(event)
    if uid:
        if event.msg['peer_id']< 2000000000:
            event.msg_op(2, '❗ Работает только в чатах.')
        else:
            chat_id=event.msg['peer_id'] - 2000000000
            try:
                event.api('messages.addChatUser', chat_id=chat_id, user_id=uid)
                event.msg_op(3)
            except VkApiResponseException as e:
                if e.error_code == 15:
                    if 'already' in e.error_msg:
                        event.msg_op(2, '🤔 Пользователь уже в беседе')
                    else:
                        event.msg_op(2, f'❗ Невозможно добавить указанного пользователя. Может он не в друзьях?')
                else:
                    event.msg_op(2, f'❗ Ошибка VK: {e.error_msg}')
    else:
        event.msg_op(2, '❗ Необходимо упоминание или ответ на сообщение')
    return 'ok'

@dp.longpoll_event_register('кик')
@dp.my_signal_event_register('кик')
def kick_user_from_chat(event: MySignalEvent):
    if get_index(event.args, 0)=='меня':
        uid=event.db.owner_id
    else:
        uid=find_mention_by_event(event)
    if uid:
        if event.msg['peer_id']< 2000000000:
            event.msg_op(2, '❗ Работает только в чатах.')
        else:
            chat_id = event.msg['peer_id'] - 2000000000
            try:
                event.api('messages.removeChatUser', chat_id=chat_id, user_id=uid)
                if uid != event.db.owner_id:
                    event.msg_op(3)
            except VkApiResponseException as e:
                if e.error_code == 15:
                    event.msg_op(2, f'❗ Невозможно удалить указанного пользователя. Может не хватает прав в беседе?')
                elif e.error_code == 935:
                    event.msg_op(2, f'❗ В этой беседе нет указанного пользователя')
                else:
                    event.msg_op(2, f'❗ Ошибка VK: {e.error_msg}')
    else:
        event.msg_op(2, '❗ Необходимо упоминание или ответ на сообщение')

@dp.longpoll_event_register('+аватарка')
@dp.my_signal_event_register('+аватарка')
def set_cover(event: MySignalEvent):
    if event.msg['peer_id']< 2000000000:
        event.msg_op(2, '❗ Работает только в чатах.')
    else:
        attachment=event.msg['attachments']
        if len(attachment)==0:
            event.msg_op(2, '🤔 И какая же аватарка?')
        elif len(attachment)>1:
            event.msg_op(2, '❗ Прикрепи только одно вложение.')
        else:
            if attachment[0]['type']=='photo':
                try:
                    orig_cover=f"photo{attachment[0]['photo']['owner_id']}_{attachment[0]['photo']['id']}"
                    chat_id=event.msg['peer_id'] - 2000000000
                    link=attachment[0]['photo']['sizes'][-1]['url'] # поговаривают что, если не программист попытается прочесть эту строчку, то мозг расплавится. Можете проверить! p.s словарная многоножка :D
                    image = io.BytesIO(requests.get(url = link).content)
                    image.name = 'cover.jpg'
                    upload_url=event.api('photos.getChatUploadServer', chat_id=chat_id)['upload_url']
                    file=requests.post(upload_url, files= {'file': image}).json()['response']
                    event.api('messages.setChatPhoto', file=file)
                    event.msg_op(2, 'Аватарка беседы изменена на:', attachment=orig_cover)
                except VkApiResponseException as e:
                    event.msg_op(2, f'❗ Невозможно установить аватарку. Может не хватает прав в беседе?')
            else:
                event.msg_op(2, '🤨 Это не фотография!')

@dp.longpoll_event_register('-аватарка')
@dp.my_signal_event_register('-аватарка')
def delete_cover(event: MySignalEvent):
    if event.msg['peer_id']< 2000000000:
        event.msg_op(2, '❗ Работает только в чатах.')
    else:
        chat_id=event.msg['peer_id'] - 2000000000
        try:
            event.api('messages.deleteChatPhoto', chat_id=chat_id)
            event.msg_op(2, '✅  Аватарка беседы удалена!')
        except VkApiResponseException as e:
            event.msg_op(2, f'❗ Невозможно удалить аватарку. Может не хватает прав в беседе?')

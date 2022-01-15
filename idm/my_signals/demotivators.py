from idm.utils import att_parse
from idm.objects import MySignalEvent, dp
from simpledemotivators import Demotivator
import requests, time, os


@dp.my_signal_event_register('дем')
def template_create(event: MySignalEvent) -> str:
    if not (event.attachments or event.reply_message):
        event.msg_op(2, "❗ Нет данных")
        return "ok"

    if event.reply_message:
        event.attachments = event.reply_message['attachments']
        print(event.attachments)
        if event.attachments:
            if event.attachments[0]['type'] == 'audio_message':
                event.msg_op(2, 'Как я тебе не из картинки сделаю демотиватор?')
                return "ok"
            url = event.attachments[0]['photo']['sizes'][-1]['url']
    else:
        if event.msg['attachments'][0]['type'] == 'audio_message':
            event.msg_op(2, 'Как я тебе не из картинки сделаю демотиватор?')
            return "ok"
        url = event.msg['attachments'][0]['photo']['sizes'][-1]['url']
    r = requests.get(url)
    name = str(int(time.time())) + '.jpg'
    out = open(name, "wb")
    out.write(r.content)
    out.close()
    args = event.msg['text'].split('\n')
    args.append('')
    try:
        dem = Demotivator(args[1], args[2])
        dem.create(name)
    except:
        text1 = 'А чё писать то?'
        dem = Demotivator(text1, '')
        dem.create(name)
    upload_url = event.api('photos.getMessagesUploadServer')['upload_url']
    uploaded = requests.post(upload_url, files={'photo': open('demresult.jpg', 'rb')}).json()
    a = event.api('photos.saveMessagesPhoto', server=uploaded["server"], photo=uploaded["photo"], hash=uploaded["hash"])[0]
    event.msg_op(2, '', attachment=f'photo{a["owner_id"]}_{a["id"]}')
    os.remove(name)
    os.remove('demresult.jpg')
    return "ok"


import requests
import datetime
import traceback
from duty.objects import dp, MySignalEvent
from duty.objects.dispatcher import MySignalDispatcher
dp = MySignalDispatcher()

@dp.longpoll_event_register('погода')
@dp.my_signal_event_register('погода')
def get_weather(event: MySignalEvent) -> str:
    city = " ".join(event.args)
    if not city:
        event.msg_op(2, "❗ Не указан город")
    else:
        try:
            data = requests.get(
                f'http://api.openweathermap.org/data/2.5/weather',
                params={'q': city, 'appid': "8ccf72ecedd6eb76311755cb76799810", 'units': 'metric', 'lang': 'ru'}
            ).json()
            if data["cod"] == "404":
                text = "❗ Город не найден"
            else:
                text = f"""
                💬 Погода в {data['name']}

                🌡️ Температура: {data['main']['temp']}°С
                ☀️ Ощущается как: {data['main']['feels_like']}°С
                ❄️ Макс/мин: {data['main']['temp_max']}°С/{data['main']['temp_min']}°С
                ☁️ Погода: {data['weather'][0]['description'].capitalize()}
                🌀 Ветер: {data['wind']['speed']} м/с
                💧 Влажность: {data['main']['humidity']}%

                🌆 Закат: {str(datetime.datetime.fromtimestamp(data['sys']['sunset']))[11:]}
                🌅 Рассвет: {str(datetime.datetime.fromtimestamp(data['sys']['sunrise']))[11:]}

                ☄ Давление: {data['main']['pressure']} мбар
                👀 Видимость: {data['visibility']}м""".replace("                ", "")

            event.msg_op(2, f'{text}')
        except Exception:
            print(traceback.format_exc())
    return "ok"
from duty.objects import dp
from duty.objects.dispatcher import IrisCBAPIDispatcher
dp = IrisCBAPIDispatcher()


@dp.event_register('ping')
def ping(event) -> str:
    try:
        __import__('uwsgi').reload()
    except ImportError:
        pass
    return "ok"

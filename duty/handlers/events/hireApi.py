from duty.objects import dp, BaseEvent
from duty.objects.dispatcher import IrisCBAPIDispatcher
dp = IrisCBAPIDispatcher()


@dp.event_register('hireApi')
def hire(event: BaseEvent) -> str:
        return {"response":"ok","days":event.obj['price']}
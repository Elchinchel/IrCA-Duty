
from duty.objects import dp, BaseEvent
from duty.objects.dispatcher import IrisCBAPIDispatcher
dp = IrisCBAPIDispatcher()


@dp.event_register('forbiddenLinks')
def forbidden_links(event: BaseEvent) -> str:
    return "ok"

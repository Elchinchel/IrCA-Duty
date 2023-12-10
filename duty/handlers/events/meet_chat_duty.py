from duty.objects import dp, BaseEvent
from duty.objects.dispatcher import IrisCBAPIDispatcher
dp = IrisCBAPIDispatcher()


@dp.event_register('meetChatDuty')
def meet_chat_duty(event: BaseEvent) -> str:
    return "ok"  # TODO: надо сюда че нить придумать

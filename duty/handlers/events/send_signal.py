from duty.objects import dp, BaseEvent, SignalEvent
from duty.objects.dispatcher import IrisCBAPIDispatcher
dp = IrisCBAPIDispatcher()


@dp.event_register('sendSignal')
def send_signal(event: BaseEvent):
    return dp.signal_event_run(SignalEvent(event))

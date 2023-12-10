from duty.objects import dp, BaseEvent, MySignalEvent
from duty.objects.dispatcher import IrisCBAPIDispatcher
dp = IrisCBAPIDispatcher()


@dp.event_register('sendMySignal')
def send_my_signal(event: BaseEvent):
    return dp.my_signal_event_run(MySignalEvent(event))

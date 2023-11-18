from duty.objects import dp, BaseEvent, MySignalEvent


@dp.event_register('sendMySignal')
def send_my_signal(event: BaseEvent):
    return dp.my_signal_event_run(MySignalEvent(event))

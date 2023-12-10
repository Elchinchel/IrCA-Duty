from duty.objects import dp, MySignalEvent
from duty.objects.dispatcher import MySignalDispatcher
dp = MySignalDispatcher()


@dp.my_signal_event_register('зам', 'замени', 'з')
def replace(event: MySignalEvent) -> str:
    text = " ".join(event.args)
    if event.args[0] == 'помощь':
        text = 'здесь будет помощь по команде'
    else:
        text = text.replace('клоун', '🤡')
        text = text.replace('клкл', '👍🏻')
        text = text.replace('кркр', '😎')
        text = text.replace('мдаа', '😐')
        text = text.replace('хмхм', '🤔')
    event.msg_op(2, text)
    return "ok"

from duty.objects import dp, BaseEvent


@dp.event_register('forbiddenLinks')
def forbidden_links(event: BaseEvent) -> str:
    return "ok"

from duty.objects import dp, BaseEvent


@dp.event_register('hireApi')
def hire(event: BaseEvent) -> str:
        return {"response":"ok","days":event.obj['price']}
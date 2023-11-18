__version__ = '__неизвестно__z'


from duty.objects import dispatcher as dp
from duty.objects.chat import Chat
from duty.objects.message import Message
from duty.objects.database import db
from duty.objects.events import (
    BaseEvent,
    SignalEvent,
    MySignalEvent,
    LongpollEvent
)

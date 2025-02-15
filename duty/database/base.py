import json

from sqlalchemy import Text, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase, MappedAsDataclass):
    ...


class AsJson(TypeDecorator[Text]):
    impl = Text
    cache_ok = False

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if not isinstance(value, str):
            raise ValueError('String expected, got %r (%r)', type(value), value)
        return json.loads(value)

from typing import Mapping

from duty.database.json_file import JsonFile
from duty.database.repository.response.base import BaseResponseRepository


class JsonFileResponseRepository(BaseResponseRepository):
    def __init__(self, json_file: JsonFile, defaults: dict[str, str]) -> None:
        self.json_file = json_file
        self.defaults = defaults

    def must_get(self, key: str) -> str:
        data = self.json_file.read()
        value = data.get(key)
        if value is None:
            value = self.defaults[key]
        return value

    def get_all(self) -> Mapping[str, str]:
        data = self.json_file.read()
        for k, v in self.defaults.items():
            if k not in data:
                data[k] = v
        return data

    def set(self, key: str, value: str):
        with self.json_file.write_context as ctx:
            data = ctx.read()
            data[key] = value
            ctx.write(data)

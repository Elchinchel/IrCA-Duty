from __future__ import annotations

import abc
import contextlib
import dataclasses
import typing

import requests

from demapi.connector.file import File


class BaseSyncConnector(abc.ABC):
    @classmethod
    @contextlib.contextmanager
    @abc.abstractmethod
    def new(cls) -> typing.Iterator[BaseSyncConnector]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def post(
        self, url: str, data: typing.Dict[str, typing.Any], file: File
    ) -> bytes:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get(self, url: str) -> bytes:
        pass  # pragma: no cover


@dataclasses.dataclass
class RequestsConnector(BaseSyncConnector):
    session: requests.Session

    @classmethod
    @contextlib.contextmanager
    def new(cls) -> typing.Iterator[RequestsConnector]:
        session = requests.Session()
        self = cls(session=session)
        with session:
            yield self

    def post(
        self, url: str, data: typing.Dict[str, typing.Any], file: File
    ) -> bytes:
        file_obj = {file.multipart_name: (file.name, file.content)}
        return self.session.post(
            url,
            data=data,
            files=file_obj,
        ).content

    def get(self, url: str) -> bytes:
        return self.session.get(url).content

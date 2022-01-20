import dataclasses
import typing

from demapi.connector.file import File


@dataclasses.dataclass
class RequestPayload:
    data: typing.Dict[str, typing.Any]
    file: File

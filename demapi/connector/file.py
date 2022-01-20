import dataclasses
import typing


@dataclasses.dataclass
class File:
    content: bytes
    name: str = "a.png"
    multipart_name: str = "uploadfile"

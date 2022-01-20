import base64
import dataclasses
import os
import re
import typing

from demapi.configure.payload import RequestPayload
from demapi.connector.coroutine import BaseAsyncConnector
from demapi.connector.sync import BaseSyncConnector
from demapi.exceptions import ImageNotFoundError


@dataclasses.dataclass
class GeneratedImage:
    content: bytes
    url: str

    def save(
        self,
        fp: typing.Union[
            str, bytes, "os.PathLike[str]", "os.PathLike[bytes]", int
        ],
    ) -> None:
        with open(fp, "wb") as file:
            file.write(self.content)

    def as_base64(self) -> bytes:
        return base64.b64encode(self.content)


@dataclasses.dataclass
class Loader:
    response_type: typing.Type[GeneratedImage] = GeneratedImage
    base_uri: str = "https://www.imgonline.com.ua/"
    preview_page_url: str = "demotivational-poster-result.php"
    image_url_pattern: typing.Pattern[bytes] = re.compile(
        rb"download\.php\?"
        b"file=result_img/"
        rb"imgonline-com-ua-(?:Dem|M)otivator-\S+\.jpg"
    )

    def download(
        self, payload: RequestPayload, connector: BaseSyncConnector
    ) -> GeneratedImage:
        preview_page = connector.post(
            self.base_uri + self.preview_page_url,
            data=payload.data,
            file=payload.file,
        )
        image_url = self._fetch_image_url(preview_page)
        image_bytes = connector.get(image_url)
        return GeneratedImage(image_bytes, image_url)

    async def coroutine_download(
        self, payload: RequestPayload, connector: BaseAsyncConnector
    ) -> GeneratedImage:
        preview_page = await connector.post(
            self.base_uri + self.preview_page_url,
            data=payload.data,
            file=payload.file,
        )
        image_url = self._fetch_image_url(preview_page)
        image_bytes = await connector.get(image_url)
        return GeneratedImage(image_bytes, image_url)

    def _fetch_image_url(self, preview_page: bytes) -> str:
        match_obj = self.image_url_pattern.search(preview_page)
        if match_obj is None:
            raise ImageNotFoundError()
        return self.base_uri + match_obj.group(0).decode("UTF-8")

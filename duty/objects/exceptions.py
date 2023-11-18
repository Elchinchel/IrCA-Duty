from duty.dto.iris import IrisCBAPIErrorCode


class IrisCBAPIError(Exception):
    def __init__(self, code: IrisCBAPIErrorCode) -> None:
        self.code = code


class HandlingError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

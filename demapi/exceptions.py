import dataclasses


@dataclasses.dataclass
class ImageNotFoundError(ValueError):
    text: str = (
        "Something happened wrong while "
        "photo was converted. "
        "Perhaps you pass an invalid image"
    )


@dataclasses.dataclass
class InvalidPhotoTypeError(TypeError):
    photo_type: type
    text: str = "Invalid photo type passed"

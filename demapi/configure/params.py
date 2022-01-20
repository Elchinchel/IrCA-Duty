import enum


class PictureType(enum.Enum):
    MOTIVATOR = enum.auto()
    DEMOTIVATOR = enum.auto()


class Color(enum.Enum):
    WHITE = enum.auto()
    RED = enum.auto()
    ORANGE = enum.auto()
    YELLOW = enum.auto()
    GREEN = enum.auto()
    LIGHT_BLUE = enum.auto()
    BLUE = enum.auto()
    PURPLE = enum.auto()
    BLACK = enum.auto()


class Size(enum.Enum):
    LARGE = enum.auto()
    BIG = enum.auto()
    AUTO = enum.auto()
    SMALL = enum.auto()
    TINY = enum.auto()


class ImageFormat(enum.Enum):
    JPEG = 2
    PNG_24 = 3


class JPEGType(enum.Enum):
    STANDARD = enum.auto()
    PROGRESSIVE = enum.auto()

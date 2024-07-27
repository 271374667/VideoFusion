from enum import Enum, auto


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Rotation(Enum):
    CLOCKWISE = 90
    COUNTERCLOCKWISE = 270
    UPSIDE_DOWN = 180
    NOTHING = 0


class FileProcessType(Enum):
    UNPROCESSED = 0
    PROCESSING = auto()
    FAILED = auto()
    FINISHED = auto()

from enum import Enum


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
    PROCESSING = 1
    FAILED = 2
    COMPLETED = 3

from enum import Enum


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Rotation(Enum):
    CLOCKWISE = 0
    COUNTERCLOCKWISE = 1
    UPSIDE_DOWN = 2
    NOTHING = 3

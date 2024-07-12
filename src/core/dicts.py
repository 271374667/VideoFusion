from pathlib import Path
from typing_extensions import NotRequired, TypedDict

from src.core.datacls import CropInfo
from src.core.enums import Orientation


class VideoInfoDict(TypedDict):
    rotation_angle: NotRequired[int]
    orientation: NotRequired[Orientation]

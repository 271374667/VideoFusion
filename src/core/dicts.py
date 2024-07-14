from typing_extensions import NotRequired, TypedDict

from src.core.enums import Orientation


class VideoInfoDict(TypedDict):
    rotation_angle: NotRequired[int]
    orientation: NotRequired[Orientation]
    target_width: NotRequired[int]
    target_height: NotRequired[int]

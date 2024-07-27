from pathlib import Path

from typing_extensions import NotRequired, TypedDict

from src.core.enums import Orientation


class VideoInfoDict(TypedDict):
    rotation_angle: NotRequired[int]
    orientation: NotRequired[Orientation]
    target_width: NotRequired[int]
    target_height: NotRequired[int]
    crop_x: NotRequired[int]
    crop_y: NotRequired[int]
    crop_width: NotRequired[int]
    crop_height: NotRequired[int]


class FileProcessDict(TypedDict):
    input_video_path: Path
    output_video_path: Path
    engine_type: int
    video_info: VideoInfoDict

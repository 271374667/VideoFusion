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

    # 视频原本的信息
    fps: NotRequired[int]
    width: NotRequired[int]
    height: NotRequired[int]
    total_frames: NotRequired[int]


class TaskDict(TypedDict):
    input_video_path: str
    task_status: int
    output_video_path: NotRequired[str]

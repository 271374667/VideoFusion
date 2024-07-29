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
    # 下面其实是VideoInfoDict的内容,不过替换了枚举类
    rotation_angle: NotRequired[int]
    orientation: NotRequired[int]
    target_width: NotRequired[int]
    target_height: NotRequired[int]
    crop_x: NotRequired[int | None]
    crop_y: NotRequired[int | None]
    crop_width: NotRequired[int | None]
    crop_height: NotRequired[int | None]


class TaskResumerDict(TypedDict):
    engine_type: int
    total_task_status: int  # 所有任务的状态,如果有一个任务失败则为失败
    task_info: list[TaskDict]

from pathlib import Path

from src.core.dicts import TaskDict
from src.core.enums import FileProcessType, Orientation, Rotation


class TaskResumer:
    def __init__(self, input_video_path: Path,
                 task_status: FileProcessType = FileProcessType.UNPROCESSED):
        self._current_status: FileProcessType = task_status
        self._data_dict: TaskDict = {
                "input_video_path": str(input_video_path),
                "task_status": task_status.value,
                }

    def get_current_status(self) -> FileProcessType:
        return self._current_status

    def get_data_dict(self) -> TaskDict:
        return self._data_dict

    def get_input_video_path(self) -> Path:
        return Path(self._data_dict.get("input_video_path"))

    def get_rotation_angle(self) -> Rotation:
        rotation = self._data_dict.get("rotation_angle")
        if rotation is None:
            raise ValueError("Rotation angle is not set")
        return Rotation(rotation)

    def get_orientation(self) -> Orientation:
        orientation = self._data_dict.get("orientation")
        if orientation is None:
            raise ValueError("Orientation is not set")
        return Orientation(orientation)

    def get_target_width(self) -> int:
        target_width = self._data_dict.get("target_width")
        if target_width is None:
            raise ValueError("Target width is not set")
        return target_width

    def get_target_height(self) -> int:
        target_height = self._data_dict.get("target_height")
        if target_height is None:
            raise ValueError("Target height is not set")
        return target_height

    def get_crop_x(self) -> int | None:
        return self._data_dict.get("crop_x")

    def get_crop_y(self) -> int | None:
        return self._data_dict.get("crop_y")

    def get_crop_width(self) -> int | None:
        return self._data_dict.get("crop_width")

    def get_crop_height(self) -> int | None:
        return self._data_dict.get("crop_height")

    def set_data_dict(self, data_dict: TaskDict):
        self._data_dict = data_dict
        self._current_status = FileProcessType(data_dict["task_status"])

    def set_status_unprocessed(self):
        self._current_status = FileProcessType.UNPROCESSED
        self._data_dict["task_status"] = FileProcessType.UNPROCESSED.value

    def set_status_processing(self):
        self._current_status = FileProcessType.PROCESSING
        self._data_dict["task_status"] = FileProcessType.PROCESSING.value

    def set_status_failed(self):
        self._current_status = FileProcessType.FAILED
        self._data_dict["task_status"] = FileProcessType.FAILED.value

    def set_status_completed(self):
        self._current_status = FileProcessType.COMPLETED
        self._data_dict["task_status"] = FileProcessType.COMPLETED.value

    def set_rotation_angle(self, rotation_angle: int):
        self._data_dict["rotation_angle"] = rotation_angle

    def set_orientation(self, orientation: int | Orientation):
        if isinstance(orientation, Orientation):
            self._data_dict["orientation"] = orientation.value
        else:
            self._data_dict["orientation"] = orientation

    def set_target_width(self, target_width: int):
        self._data_dict["target_width"] = target_width

    def set_target_height(self, target_height: int):
        self._data_dict["target_height"] = target_height

    def set_crop_x(self, crop_x: int):
        self._data_dict["crop_x"] = crop_x

    def set_crop_y(self, crop_y: int):
        self._data_dict["crop_y"] = crop_y

    def set_crop_width(self, crop_width: int):
        self._data_dict["crop_width"] = crop_width

    def set_crop_height(self, crop_height: int):
        self._data_dict["crop_height"] = crop_height

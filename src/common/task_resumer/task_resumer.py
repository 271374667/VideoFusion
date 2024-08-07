from pathlib import Path

from src.core.dicts import TaskDict
from src.core.enums import FileProcessType


class TaskResumer:
    def __init__(self, input_video_path: Path,
                 task_status: FileProcessType = FileProcessType.UNCOMPLETED,
                 ):
        self._current_status: FileProcessType = task_status
        self._data_dict: TaskDict = {
                "input_video_path": str(input_video_path),
                "task_status": task_status.value,
                }

    @property
    def input_video_path(self) -> Path:
        return Path(self._data_dict["input_video_path"])

    @input_video_path.setter
    def input_video_path(self, value: Path):
        self._data_dict["input_video_path"] = str(value)

    @property
    def current_status(self) -> FileProcessType:
        return self._current_status

    @current_status.setter
    def current_status(self, value: FileProcessType):
        self._current_status = value
        self._data_dict["task_status"] = value.value

    @property
    def data_dict(self) -> TaskDict:
        return self._data_dict

    @data_dict.setter
    def data_dict(self, value: TaskDict):
        self._data_dict = value
        self._current_status = FileProcessType(value["task_status"])

    @property
    def output_video_path(self) -> Path | None:
        output_video_path = self._data_dict.get("output_video_path")
        return None if output_video_path is None else Path(output_video_path)

    @output_video_path.setter
    def output_video_path(self, value: Path):
        if not value.exists():
            raise FileNotFoundError(f"Output video path {value} does not exist")
        self._data_dict["output_video_path"] = str(value)
        self.current_status = FileProcessType.COMPLETED

    def __repr__(self):
        return f"TaskResumer({self.input_video_path}, {self.current_status})"

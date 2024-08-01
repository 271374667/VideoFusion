import json
from pathlib import Path

import loguru

from src.common.task_resumer.task_resumer import TaskResumer
from src.config import VideoProcessEngine, cfg
from src.core.dicts import TaskResumerDict
from src.core.enums import FileProcessType
from src.core.enums import Orientation, Rotation
from src.core.paths import RESUME_FILE
from src.utils import singleton


@singleton
class TaskResumerManager:
    def __init__(self, engine_type: VideoProcessEngine,
                 orientation: Orientation,
                 rotation: Rotation
                 ):
        self._task_index: int = 0

        self._resume_file_path: Path = RESUME_FILE
        self._current_task: TaskResumer | None = None
        self._task_list: list[TaskResumer] = []
        self._total_task_status: FileProcessType = FileProcessType.UNPROCESSED

        self._task_resumer_dict: TaskResumerDict = {
                "engine_type": engine_type.value,
                "total_task_status": 0,
                "orientation": orientation.value,
                "rotation_angle": rotation.value,
                "task_info": []
                }

    def append_task(self, task: TaskResumer):
        self._task_list.append(task)
        self._task_resumer_dict["task_info"].append(task.get_data_dict())

    def get_current_task(self) -> TaskResumer | None:
        return self._current_task

    def get_task_list(self) -> list[TaskResumer]:
        return self._task_list

    def get_total_task_status(self) -> FileProcessType:
        return self._total_task_status

    def get_uncompleted_task_list(self) -> list[TaskResumer]:
        return [task for task in self._task_list if task.get_current_status() != FileProcessType.COMPLETED]

    def set_current_task(self, task: TaskResumer):
        self._current_task = task

    def set_total_task_status(self, status: FileProcessType):
        self._total_task_status = status
        self._task_resumer_dict["total_task_status"] = status.value

    def set_total_task_status_unprocessed(self):
        self._total_task_status = FileProcessType.UNPROCESSED
        self._task_resumer_dict["total_task_status"] = FileProcessType.UNPROCESSED.value

    def set_total_task_status_processing(self):
        self._total_task_status = FileProcessType.PROCESSING
        self._task_resumer_dict["total_task_status"] = FileProcessType.PROCESSING.value

    def set_total_task_status_failed(self):
        self._total_task_status = FileProcessType.FAILED
        self._task_resumer_dict["total_task_status"] = FileProcessType.FAILED.value

    def set_total_task_status_completed(self):
        self._total_task_status = FileProcessType.COMPLETED
        self._task_resumer_dict["total_task_status"] = FileProcessType.COMPLETED.value

    def save(self):
        """保存为json"""
        with open(self._resume_file_path, "w") as f:
            json.dump(self._task_resumer_dict, f)

    def load(self) -> list[TaskResumer]:
        """从json加载"""
        if not self._resume_file_path.exists():
            self.save()

        with open(self._resume_file_path, "r") as f:
            self._task_resumer_dict = json.load(f)
            self._total_task_status = FileProcessType(self._task_resumer_dict["total_task_status"])
            for task_dict in self._task_resumer_dict["task_info"]:
                task_resumer = TaskResumer(task_dict["input_video_path"], task_dict["output_video_path"])
                task_resumer.set_data_dict(task_dict)
                self._task_list.append(task_resumer)
        loguru.logger.debug(f"加载任务恢复文件:{self._resume_file_path},任务数:{len(self._task_list)}")
        return self._task_list

    def check_last_task_completed(self) -> bool:
        """读取本地文件，检查上次任务是否完成"""
        if self._resume_file_path.exists():
            with open(self._resume_file_path, "r") as f:
                task_resumer_dict = json.load(f)
                total_task_status = FileProcessType(task_resumer_dict["total_task_status"])
                return total_task_status == FileProcessType.COMPLETED
        return True

    def remove(self, task: TaskResumer):
        """删除任务"""
        self._task_list.remove(task)
        self._task_resumer_dict["task_info"].remove(task.get_data_dict())
        loguru.logger.debug(f"删除任务{task.get_input_video_path()}")

    def clear(self):
        """清空任务"""
        self._task_list.clear()
        self._task_resumer_dict["task_info"].clear()
        self._total_task_status = FileProcessType.UNPROCESSED
        self._task_resumer_dict["total_task_status"] = FileProcessType.UNPROCESSED.value
        self.save()
        loguru.logger.debug("清空任务恢复文件")

    def is_temp_dir_empty(self) -> bool:
        """判断临时文件夹是否为空来变相检查任务是否可以恢复"""
        temp_dir = Path(cfg.get(cfg.temp_dir))
        return not any(temp_dir.iterdir()) if temp_dir.exists() else True

    def is_completed(self) -> bool:
        """判断是否完成"""
        return self._total_task_status == FileProcessType.COMPLETED

    def is_json_exist(self) -> bool:
        """判断json文件是否存在"""
        return self._resume_file_path.exists()

    def __iter__(self):
        return self

    def __next__(self) -> TaskResumer:
        if self._task_index >= len(self._task_list):
            raise StopIteration
        task = self._task_list[self._task_index]
        self._task_index += 1
        return task

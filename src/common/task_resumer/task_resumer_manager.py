import json
from pathlib import Path

import loguru

from src.common.task_resumer.task_resumer import TaskResumer
from src.core.dicts import TaskDict
from src.core.enums import FileProcessType
from src.core.paths import RESUME_FILE
from src.utils import singleton


@singleton
class TaskResumerManager:
    def __init__(self):
        self._resume_file_path: Path = RESUME_FILE
        self._task_list: list[TaskResumer] = []

        if self.finished:
            self.clear()
            self.save()
        else:
            self.load()

    @property
    def resume_file_path(self) -> Path:
        return self._resume_file_path

    @resume_file_path.setter
    def resume_file_path(self, value: Path):
        self._resume_file_path = value

    @property
    def task_list(self) -> list[TaskResumer]:
        return self._task_list

    @property
    def total_task_status(self) -> FileProcessType:
        if all(task.current_status == FileProcessType.COMPLETED for task in self._task_list):
            return FileProcessType.COMPLETED
        return FileProcessType.UNCOMPLETED

    @total_task_status.setter
    def total_task_status(self, value: FileProcessType):
        for task in self._task_list:
            task.current_status = value

    @property
    def uncompleted_task_list(self) -> list[TaskResumer]:
        return [task for task in self._task_list if task.current_status != FileProcessType.COMPLETED]

    @property
    def finished(self) -> bool:
        return all(task.current_status == FileProcessType.COMPLETED for task in self._task_list)

    def append_task(self, task: TaskResumer):
        self._task_list.append(task)

    def save(self):
        """保存为json"""
        with open(self._resume_file_path, "w") as f:
            json.dump([x.data_dict for x in self._task_list], f)

    def load(self) -> list[TaskResumer]:
        """从json加载"""
        if not self._resume_file_path.exists():
            self.save()

        with open(self._resume_file_path, "r") as f:
            resume_data: list[TaskDict] = json.load(f)
            for each_task in resume_data:
                task_resumer = TaskResumer(Path(each_task['input_video_path']),
                                           FileProcessType(each_task['task_status']))
                self._task_list.append(task_resumer)
        loguru.logger.debug(f"加载任务恢复文件:{self._resume_file_path},任务数:{len(self._task_list)}")
        return self._task_list

    def remove(self, task: TaskResumer):
        """删除任务"""
        self._task_list.remove(task)
        loguru.logger.debug(f"删除任务{task}")

    def clear(self):
        """清空任务"""
        self._task_list.clear()
        loguru.logger.debug("清空任务恢复文件")

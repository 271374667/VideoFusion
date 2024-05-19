from concurrent.futures import ThreadPoolExecutor

import loguru
from PySide6.QtCore import QObject

from src.core.enums import Orientation, Rotation
from src.main import VideoMosaic


class Worker(QObject):
    def start(self,
              is_dir: bool,
              dir_or_file: str,
              output_file: str,
              dir_mode: str,
              fps: int,
              sample_rate: float,
              video_orientation: Orientation,
              horizontal_rotation: Rotation,
              vertical_rotation: Rotation):
        vm = VideoMosaic()
        if is_dir:
            vm.add_video_dir(dir_or_file, dir_mode)
        else:
            vm.read_from_txt_file(dir_or_file)

        vm.output_file_path = output_file
        vm.fps = fps
        vm.sample_rate = sample_rate
        vm.video_orientation = video_orientation
        vm.horizontal_rotation = horizontal_rotation
        vm.vertical_rotation = vertical_rotation
        vm.start()


class HomeModel:
    def __init__(self):
        self._pool = ThreadPoolExecutor(3)
        self._worker = Worker()

    def start(self,
              is_dir: bool,
              dir_or_file: str,
              output_file: str,
              dir_mode: str,
              fps: int,
              sample_rate: float,
              video_orientation: Orientation,
              horizontal_rotation: Rotation,
              vertical_rotation: Rotation
              ):
        loguru.logger.info("程序开始执行……")
        self._pool.submit(self._worker.start, is_dir, dir_or_file, output_file, dir_mode, fps, sample_rate,
                          video_orientation, horizontal_rotation, vertical_rotation)

from concurrent.futures import ThreadPoolExecutor

import loguru
from PySide6.QtCore import QObject

from src.core.enums import Orientation, Rotation
from src.main import VideoMosaic


class Worker(QObject):
    def start_job(self,
                  is_dir: bool,
                  dir_or_file: str,
                  output_file: str,
                  dir_mode: str,
                  fps: int,
                  sample_rate: float,
                  video_orientation: Orientation,
                  horizontal_rotation: Rotation,
                  vertical_rotation: Rotation):
        self._vm = VideoMosaic()
        if is_dir:
            self._vm.add_video_dir(dir_or_file, dir_mode)
        else:
            self._vm.read_from_txt_file(dir_or_file)

        self._vm.output_dir = output_file
        self._vm.fps = fps
        self._vm.sample_rate = sample_rate
        self._vm.video_orientation = video_orientation
        self._vm.horizontal_rotation = horizontal_rotation
        self._vm.vertical_rotation = vertical_rotation
        self._vm.start()


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
        self._pool.submit(
            lambda: self._worker.start_job(is_dir, dir_or_file, output_file, dir_mode, fps, round(sample_rate, 2),
                                           video_orientation, horizontal_rotation, vertical_rotation))
        loguru.logger.debug(f'参数: {is_dir=}, {dir_or_file=}, {output_file=}, {dir_mode=}, {fps=}, {sample_rate=}, ')

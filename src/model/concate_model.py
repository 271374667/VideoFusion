from pathlib import Path

import loguru
from PySide6.QtCore import QObject

from src.common.program_coordinator import ProgramCoordinator
from src.config import cfg
from src.core.enums import Orientation, Rotation
from src.signal_bus import SignalBus
from src.utils import ForceStopThread


class Worker(QObject):
    def __init__(self):
        super().__init__()
        self._signal_bus = SignalBus()
        self._program_coordinator = ProgramCoordinator()

    def start(self, video_list: list[Path], video_orientation: Orientation, video_rotation: Rotation):
        self._program_coordinator.process(video_list, video_orientation, video_rotation)


class ConcateModel:
    def __init__(self):
        self._signal_bus = SignalBus()
        self._worker = Worker()
        self._force_stop_thread = ForceStopThread()

    @property
    def merge_video_enabled(self) -> bool:
        return cfg.get(cfg.merge_video)

    def kill_thread(self):
        self._signal_bus.set_running.emit(False)
        self._force_stop_thread.stop_task()
        loguru.logger.info('程序被强制停止')

    def start(self, video_list: list[str | Path], video_orientation: Orientation, video_rotation: Rotation):
        video_list: list[Path] = [Path(video) for video in video_list if Path(video).exists()]
        self._force_stop_thread.start_task(self._worker.start, video_list, video_orientation, video_rotation)
        loguru.logger.debug(f'程序开始执行,参数如下: {video_orientation}, {video_rotation}, 视频列表为:{video_list}')


if __name__ == '__main__':
    # 绑定信号
    signal_bus = SignalBus()
    signal_bus.set_detail_progress_current.connect(lambda x: print(f'当前进度为{x}'))
    signal_bus.set_detail_progress_max.connect(lambda x: print(f'最大进度为{x}'))
    signal_bus.set_detail_progress_description.connect(lambda x: print(f'描述为{x}'))
    signal_bus.set_total_progress_current.connect(lambda x: print(f'总进度为{x}'))
    signal_bus.set_total_progress_max.connect(lambda x: print(f'总最大进度为{x}'))
    signal_bus.set_total_progress_description.connect(lambda x: print(f'总描述为{x}'))
    signal_bus.set_total_progress_reset.connect(lambda: print('总进度重置'))
    signal_bus.set_detail_progress_reset.connect(lambda: print('详细进度重置'))
    signal_bus.set_total_progress_finish.connect(lambda: print('总进度完成'))
    signal_bus.set_detail_progress_finish.connect(lambda: print('详细进度完成'))
    signal_bus.advance_total_progress.connect(lambda x: print(f'总进度增加{x}'))
    signal_bus.advance_detail_progress.connect(lambda x: print(f'详细进度增加{x}'))
    signal_bus.finished.connect(lambda: print('完成'))

    video_list = Path(r"E:\load\python\Project\VideoFusion\测试\video\1.txt").read_text(
            ).replace('"', '').splitlines()
    model = ConcateModel()
    # model.start(video_list, Orientation.HORIZONTAL, Rotation.CLOCKWISE)

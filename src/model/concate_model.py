import os
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

import loguru
from PySide6.QtCore import QObject

from src.common.ffmpeg import generate_ffmpeg_command, merge_videos, run_command
from src.common.video_info import VideoInfo, get_most_compatible_resolution, get_video_info
from src.config import cfg
from src.core.enums import Orientation, Rotation
from src.signal_bus import SignalBus
from src.utils import TempDir

signal_bus = SignalBus()
temp_dir = TempDir()
TEMP_DIR = temp_dir.get_temp_dir()


class Worker(QObject):
    def start(self, video_list: list[str | Path], video_orientation: Orientation, video_rotation: Rotation):
        loguru.logger.info(f'开始处理视频,当前一共有{len(video_list)}个视频')
        signal_bus.set_total_progress_reset.emit()
        signal_bus.set_detail_progress_reset.emit()

        # 获取所有视频文件的信息
        loguru.logger.info('开始获取视频信息')
        video_list: list[Path] = [Path(x) for x in video_list]
        signal_bus.set_total_progress_description.emit("分析视频")
        signal_bus.set_total_progress_max.emit(len(video_list))
        video_info_list: list[VideoInfo] = []
        for each in video_list:
            loguru.logger.debug(f'正在分析视频:{each.name}')
            sample_rate: int = cfg.get(cfg.video_sample_rate)
            sample: float = max(min(sample_rate / 10, 0), 1)
            video_info = get_video_info(each, sample_rate=sample)
            video_info_list.append(video_info)
            signal_bus.advance_total_progress.emit(1)
            loguru.logger.debug(f'视频分析{each.name}分析完成:{video_info}')
        loguru.logger.info(f'获取视频信息完成,一共获取到了{len(video_info_list)}个视频信息')

        # 获取最佳分辨率
        loguru.logger.debug('正在获取最佳分辨率')
        signal_bus.set_total_progress_description.emit("调优参数")
        signal_bus.set_total_progress_reset.emit()
        signal_bus.set_detail_progress_reset.emit()
        best_width, best_height = get_most_compatible_resolution(video_info_list, video_orientation)
        loguru.logger.info(f'最佳分辨率获取完成,最佳分辨率为: {best_width}x{best_height}')

        # 生成ffmpeg命令
        loguru.logger.info('正在生成ffmepg命令')
        signal_bus.set_total_progress_description.emit("生成命令")
        ffmpeg_list: list[tuple[Path, str]] = []
        output_video_list: list[Path] = []
        for each in video_info_list:
            loguru.logger.debug(f'正在生成视频:{each.video_path.name}的命令')
            # 旋转角度
            rotate_angle: int = 0
            if video_orientation == Orientation.HORIZONTAL:
                if each.crop and each.crop.w < each.crop.h:
                    rotate_angle = video_rotation.value
                elif not each.crop and each.width < each.height:
                    rotate_angle = video_rotation.value
            elif video_orientation == Orientation.VERTICAL:
                if each.crop and each.crop.w > each.crop.h:
                    rotate_angle = video_rotation.value
                elif not each.crop and each.width > each.height:
                    rotate_angle = video_rotation.value

            output_path: Path = TEMP_DIR / f'{each.video_path.stem}_output.mp4'
            if output_path.exists():
                output_path.unlink()
            output_video_list.append(output_path)
            loguru.logger.debug(
                    f'视频{each.video_path.name}的参数为: {each.crop},{best_width=},{best_height=},{rotate_angle=}')
            command = generate_ffmpeg_command(input_file=each.video_path, output_file_path=output_path,
                                              crop_position=each.crop, width=best_width, height=best_height,
                                              rotation_angle=rotate_angle)
            ffmpeg_list.append((each.video_path, command))
        loguru.logger.info('ffmepg命令生成完成')

        # 运行指令
        loguru.logger.info(f'开始处理视频,一共有{len(ffmpeg_list)}条命令等待处理')
        signal_bus.set_total_progress_description.emit("处理视频")
        signal_bus.set_total_progress_max.emit(len(ffmpeg_list))
        for each in ffmpeg_list:
            loguru.logger.debug(f'正在处理视频:{each[0].name}')
            run_command(input_file_path=each[0], command=each[1])
            signal_bus.advance_total_progress.emit(1)
        signal_bus.set_total_progress_finish.emit()
        signal_bus.set_detail_progress_finish.emit()
        loguru.logger.info('视频处理完毕')

        # 合并视频
        loguru.logger.info('开始合并视频')
        signal_bus.set_total_progress_reset.emit()
        signal_bus.set_detail_progress_reset.emit()
        signal_bus.set_total_progress_description.emit("合并视频")
        output_path = cfg.get(cfg.output_file_path)
        merge_videos(video_list=output_video_list, output_path=output_path)
        signal_bus.set_total_progress_finish.emit()
        signal_bus.set_detail_progress_finish.emit()
        signal_bus.set_total_progress_description.emit("处理完成")

        output_path = cfg.get(cfg.output_file_path)
        output_dir = Path(output_path).parent
        os.startfile(output_dir)
        loguru.logger.success(f'合并完成,文件已经输出到{cfg.get(cfg.output_file_path)}')
        signal_bus.finished.emit()


class ConcateModel:
    def __init__(self):
        self._pool: ThreadPoolExecutor = ThreadPoolExecutor(3)
        self._worker = Worker()

    def start(self, video_list: list[str | Path], video_orientation: Orientation, video_rotation: Rotation):
        f: Future = self._pool.submit(self._worker.start, video_list, video_orientation, video_rotation)
        loguru.logger.debug(f'程序开始执行,参数如下: {video_orientation}, {video_rotation}, 视频列表为:{video_list}')


if __name__ == '__main__':
    # 绑定信号
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

    video_list = Path(r"E:\load\python\Project\VideoMosaic\测试\t.txt").read_text(
            encoding="utf-8").replace('"', '').splitlines()
    model = ConcateModel()
    model.start(video_list, Orientation.HORIZONTAL, Rotation.CLOCKWISE)

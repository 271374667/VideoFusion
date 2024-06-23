import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import loguru
from PySide6.QtCore import QObject

from src.common.ffmpeg import generate_ffmpeg_command, merge_videos, run_command
from src.common.video_info import VideoInfo, get_most_compatible_resolution, get_video_info
from src.config import AudioSampleRate, cfg
from src.core.enums import Orientation, Rotation
from src.signal_bus import SignalBus
from src.utils import TempDir

signal_bus = SignalBus()
temp_dir = TempDir()
TEMP_DIR = temp_dir.get_temp_dir()


class Worker(QObject):
    def __init__(self):
        super().__init__()
        self._signal_bus = SignalBus()
        self.is_running: bool = False
        self.is_merging: bool = False
        self._signal_bus.set_running.connect(self.set_running)

    def start(self, video_list: list[str | Path], video_orientation: Orientation, video_rotation: Rotation):
        self.is_running = True
        self.is_merging = False
        self.video_list: list[Path] = [Path(x) for x in video_list if Path(x).exists()]
        self._reset_progress()
        video_info_list = self._get_video_info(self.video_list)
        if not self.is_running:
            return

        best_width, best_height = self._get_best_resolution(video_info_list, video_orientation)
        target_audio_sample_rate: int = self._get_audio_sample_rate(video_info_list)

        loguru.logger.info(f'当前音频采样率为:{target_audio_sample_rate}')

        if not self.is_running:
            return

        ffmpeg_list, output_video_list = self._generate_ffmpeg_commands(video_info_list, best_width, best_height,
                                                                        target_audio_sample_rate,
                                                                        video_orientation, video_rotation)
        if not self.is_running:
            return

        self._run_commands(ffmpeg_list)
        self._merge_videos(output_video_list)

    def _reset_progress(self):
        loguru.logger.info(f'开始处理视频,当前一共有{len(self.video_list)}个视频')
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()

    def _get_video_info(self, video_list: list[Path]) -> list[VideoInfo]:
        # 获取所有视频文件的信息
        loguru.logger.info('开始获取视频信息')
        self._signal_bus.set_total_progress_description.emit("分析视频")
        self._signal_bus.set_total_progress_max.emit(len(video_list))

        video_info_list: list[VideoInfo] = []
        for each in video_list:
            if not self.is_running:
                loguru.logger.info('用户取消了视频合并')
                break

            loguru.logger.debug(f'正在分析视频:{each.name}')
            video_info = get_video_info(each, sample_rate=0.8)  # Assuming a sample rate of 0.8
            video_info_list.append(video_info)

            self._signal_bus.advance_total_progress.emit(1)
            loguru.logger.debug(f'视频分析{each.name}分析完成:{video_info}')
        loguru.logger.info(f'获取视频信息完成,一共获取到了{len(video_info_list)}个视频信息')
        return video_info_list

    def _get_best_resolution(self, video_info_list, video_orientation) -> tuple[int, int]:
        loguru.logger.debug('正在获取最佳分辨率')
        self._signal_bus.set_total_progress_description.emit("调优参数")
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        best_width, best_height = get_most_compatible_resolution(video_info_list, video_orientation)
        loguru.logger.info(f'最佳分辨率获取完成,最佳分辨率为: {best_width}x{best_height}')
        return best_width, best_height

    def _get_audio_sample_rate(self, video_info_list: list[VideoInfo]) -> int:
        # 根据配置文件选择音频采样率
        audio_sample_rate: AudioSampleRate = cfg.get(cfg.audio_sample_rate)
        match audio_sample_rate:
            case AudioSampleRate.Hz8000:
                target_audio_sample_rate = 8000
            case AudioSampleRate.Hz16000:
                target_audio_sample_rate = 16000
            case AudioSampleRate.Hz22050:
                target_audio_sample_rate = 22050
            case AudioSampleRate.Hz32000:
                target_audio_sample_rate = 32000
            case AudioSampleRate.Hz44100:
                target_audio_sample_rate = 44100
            case AudioSampleRate.Hz96000:
                target_audio_sample_rate = 96000
            case AudioSampleRate.Max:
                audio_sample_rate_list: list[int] = [x.audio_sample_rate for x in video_info_list]
                # 获取最大的采样率
                target_audio_sample_rate = max(audio_sample_rate_list)
            case _:
                raise ValueError(f'未知的音频采样率:{audio_sample_rate}')

        return target_audio_sample_rate

    def _generate_ffmpeg_commands(self,
                                  video_info_list: list[VideoInfo],
                                  best_width: int,
                                  best_height: int,
                                  best_audio_sample_rate: int,
                                  video_orientation: Orientation,
                                  video_rotation: Rotation) -> tuple[list[tuple[Path, str]], list[Path]]:
        """
        生成ffmpeg命令

        Args:
            video_info_list: 视频信息列表
            best_width: 最佳宽度
            best_height: 最佳高度
            best_audio_sample_rate: 最佳音频采样率
            video_orientation: 视频方向
            video_rotation: 视频旋转角度

        Returns:
            list[tuple[输入视频路径,ffmpeg命令]], list[输出视频]
        """
        # 生成ffmpeg命令
        loguru.logger.info('正在生成ffmepg命令')
        self._signal_bus.set_total_progress_description.emit("生成命令")

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

            output_path: Path = Path(cfg.get(cfg.temp_dir)) / f'{each.video_path.stem}_output.mp4'
            if output_path.exists():
                output_path.unlink()

            loguru.logger.debug(
                    f'视频{each.video_path.name}的参数为: {each.crop=},{best_width=},{best_height=},{rotate_angle=}')
            output_video_list.append(output_path)
            command = generate_ffmpeg_command(input_file=each.video_path, output_file_path=output_path,
                                              crop_position=each.crop, width=best_width, height=best_height,
                                              audio_sample_rate=best_audio_sample_rate,
                                              rotation_angle=rotate_angle)
            ffmpeg_list.append((each.video_path, command))
        loguru.logger.info('ffmepg命令生成完成')
        return ffmpeg_list, output_video_list

    def _run_commands(self, ffmpeg_list):
        # 运行指令
        loguru.logger.info(f'开始处理视频,一共有{len(ffmpeg_list)}条命令等待处理')
        self._signal_bus.set_total_progress_description.emit("处理视频")
        self._signal_bus.set_total_progress_max.emit(len(ffmpeg_list))

        for each in ffmpeg_list:
            if not self.is_running:
                loguru.logger.info('用户取消了视频合并')
                return

            loguru.logger.debug(f'正在处理视频:{each[0].name}, 命令为:{each[1]}')
            run_command(input_file_path=each[0], command=each[1])
            signal_bus.advance_total_progress.emit(1)

        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        loguru.logger.info('视频处理完毕')

    def _merge_videos(self, output_video_list):
        # 合并视频
        if not self.is_running:
            loguru.logger.info('用户取消了视频合并')
            return

        self.is_merging = True

        loguru.logger.info('开始合并视频')
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_description.emit("合并视频")

        output_path = Path(cfg.get(cfg.output_file_path))
        output_dir = Path(output_path).parent
        merge_videos(video_list=output_video_list, output_path=output_path)

        os.startfile(output_dir)

        loguru.logger.success(f'合并完成,文件已经输出到{cfg.get(cfg.output_file_path)}')
        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        self._signal_bus.set_total_progress_description.emit("处理完成")
        self._signal_bus.finished.emit()

    def set_running(self, flag: bool):
        self.is_running = flag

    def __del__(self):
        temp_dir.delete_dir()
        loguru.logger.warning(f'运行完成,删除临时文件夹{temp_dir.get_temp_dir()}')


class ConcateModel:
    def __init__(self):
        self._signal_bus = SignalBus()
        self._pool: ThreadPoolExecutor = ThreadPoolExecutor(3)
        self._worker = Worker()

    @property
    def is_running(self):
        return self._worker.is_running

    @property
    def is_merging(self):
        return self._worker.is_merging

    def set_running(self, flag: bool):
        self._signal_bus.set_running.emit(flag)

    def start(self, video_list: list[str | Path], video_orientation: Orientation, video_rotation: Rotation):
        self._pool.submit(self._worker.start, video_list, video_orientation, video_rotation)
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

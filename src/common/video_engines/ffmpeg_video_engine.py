from pathlib import Path

import loguru

from src.common.ffmpeg import generate_ffmpeg_command
from src.common.ffmpeg_handler import FFmpegHandler
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.common.video_engines.base_video_engine import BaseVideoEngine
from src.config import AudioSampleRate, cfg
from src.core.datacls import CropInfo
from src.core.enums import Orientation, Rotation
from src.signal_bus import SignalBus
from src.utils import get_output_file_path


class FFmpegVideoEngine(BaseVideoEngine):
    def __init__(self):
        self.is_running: bool = False

        self._signal_bus = SignalBus()
        self._processor_global_var = ProcessorGlobalVar()

        self._ffmpeg_handler: FFmpegHandler = FFmpegHandler()
        self._signal_bus.set_running.connect(self._set_running)

    def process_video(self, input_video_path: Path) -> Path:
        self.is_running = True
        video_orientation: Orientation = self._processor_global_var.get_data()['orientation']
        video_rotation: Rotation = Rotation(self._processor_global_var.get_data()['rotation_angle'])

        best_width: int = self._processor_global_var.get_data()['target_width']
        best_height: int = self._processor_global_var.get_data()['target_height']
        target_audio_sample_rate: int = self._get_audio_sample_rate()

        loguru.logger.info(f'当前音频采样率为:{target_audio_sample_rate}')

        # 将视频信息转换为VideoInfo对象
        output_file_path = get_output_file_path(input_video_path, 'ffmpeg_processed')
        ffmpeg_command: str = self._generate_ffmpeg_commands(input_video_path,
                                                             output_file_path,
                                                             best_width,
                                                             best_height,
                                                             target_audio_sample_rate,
                                                             video_orientation, video_rotation)

        total_frames = self._ffmpeg_handler.get_video_total_frame(input_video_path)
        self._ffmpeg_handler.run_command(ffmpeg_command, total_frames)
        return output_file_path

    def _get_audio_sample_rate(self) -> int:
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
            case _:
                raise ValueError(f'未知的音频采样率:{audio_sample_rate}')

        return target_audio_sample_rate

    def _generate_ffmpeg_commands(self,
                                  input_video_path: Path,
                                  output_video_path: Path,
                                  best_width: int,
                                  best_height: int,
                                  best_audio_sample_rate: int,
                                  video_orientation: Orientation,
                                  video_rotation: Rotation) -> str:
        """
        生成ffmpeg命令

        Args:
            input_video_path: 视频信息
            best_width: 最佳宽度
            best_height: 最佳高度
            best_audio_sample_rate: 最佳音频采样率
            video_orientation: 视频方向
            video_rotation: 视频旋转角度

        Returns:
            (ffmpeg命令, 输出视频路径), 输出视频路径
        """
        crop_x = self._processor_global_var.get_data()['crop_x']
        crop_y = self._processor_global_var.get_data()['crop_y']
        crop_width = self._processor_global_var.get_data()['crop_width']
        crop_height = self._processor_global_var.get_data()['crop_height']
        original_width = self._processor_global_var.get_data()['width']
        original_height = self._processor_global_var.get_data()['height']
        crop: CropInfo | None = None
        # 如果[crop_x, crop_y, crop_width, crop_height]都不为None,则说明需要裁剪
        if (crop_x is not None
                and crop_y is not None
                and crop_width is not None
                and crop_height is not None):
            crop = CropInfo(
                    x=crop_x,
                    y=crop_y,
                    w=crop_width,
                    h=crop_height
                    )

        # 旋转角度
        rotate_angle: int = 0
        if video_orientation == Orientation.HORIZONTAL:
            if crop and crop.w < crop.h:
                rotate_angle = video_rotation.value
            elif not crop and original_width < original_height:
                rotate_angle = video_rotation.value
        elif video_orientation == Orientation.VERTICAL:
            if crop and crop.w > crop.h:
                rotate_angle = video_rotation.value
            elif not crop and original_width > original_height:
                rotate_angle = video_rotation.value

        if output_video_path.exists():
            output_video_path.unlink()

        loguru.logger.debug(
                f'视频{input_video_path}的参数为: {crop=},{best_width=},{best_height=},{rotate_angle=}')
        return generate_ffmpeg_command(
                input_file=input_video_path,
                output_file_path=output_video_path,
                crop_position=crop,
                target_width=best_width,
                target_height=best_height,
                audio_sample_rate=best_audio_sample_rate,
                rotation_angle=rotate_angle,
                )

    def _set_running(self, flag: bool):
        self.is_running = flag

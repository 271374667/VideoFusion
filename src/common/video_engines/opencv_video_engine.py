from pathlib import Path

import cv2
import loguru

from src.common.ffmpeg_handler import FFmpegHandler
from src.common.processors.audio_processors.audio_processor_manager import AudioProcessorManager
from src.common.processors.opencv_processors.opencv_processor_manager import OpenCVProcessorManager
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.common.video_engines.base_video_engine import BaseVideoEngine
from src.signal_bus import SignalBus
from src.utils import TempDir, get_output_file_path


class OpenCVVideoEngine(BaseVideoEngine):
    def __init__(self):
        self._signal_bus: SignalBus = SignalBus()
        self._temp_dir: TempDir = TempDir()
        self._ffmpeg_handler: FFmpegHandler = FFmpegHandler()
        self._audio_processor_manager: AudioProcessorManager = AudioProcessorManager()
        self._video_processor_manager: OpenCVProcessorManager = OpenCVProcessorManager()
        self._processor_global_var: ProcessorGlobalVar = ProcessorGlobalVar()

        self.is_running: bool = True
        self._signal_bus.set_running.connect(self._set_running)

    def process_video(self, input_video_path: Path) -> Path:
        if (self._processor_global_var.get_data()['crop_x'] is None
                and self._processor_global_var.get_data()['crop_y'] is None):
            self._video_processor_manager.get_crop_processor().is_enable = False

        video_after_processed = self._video_process(input_video_path)

        try:
            audio_extractor = self._ffmpeg_handler.extract_audio_from_video(input_video_path)
        except Exception as e:
            loguru.logger.error(f'提取音频失败，原因：{e}')
            audio_extractor = None

        if not audio_extractor:
            loguru.logger.debug(f'视频{input_video_path}没有音频')
            return video_after_processed
        audio_after_processed = self._audio_process(audio_extractor)

        if not self.is_running:
            raise ValueError("您暂停了程序")

        # 合并视频和音频
        video_with_audio: Path = self._ffmpeg_handler.replace_video_audio(video_after_processed, audio_after_processed)
        return self._ffmpeg_handler.reencode_video(video_with_audio)

    def _video_process(self, input_video_path: Path) -> Path:
        """
        读取输入视频，逐帧处理，然后写入输出视频,以及音频处理

        Args:
            input_video_path: 输入视频的路径
        """
        self._signal_bus.set_detail_progress_reset.emit()

        cap = cv2.VideoCapture(str(input_video_path))
        if not cap.isOpened():
            raise ValueError("无法打开输入视频")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # 因为处理后的视频的宽高可能会发生变化，所以需要重新获取宽高
        width, height = self._get_after_process_width_and_height(input_video_path)

        # MP4V比较通用，但是不支持透明度
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        output_file_path = get_output_file_path(input_video_path, "video_processed")
        out = cv2.VideoWriter(str(output_file_path), fourcc, fps, (width, height))

        self._signal_bus.set_detail_progress_max.emit(total_frames)
        for _ in range(total_frames):
            ret, frame = cap.read()
            if not ret or not self.is_running:
                break

            # 对帧进行处理
            processed_frame = self._video_processor_manager.process(frame)

            # 写入处理后的帧
            out.write(processed_frame)
            self._signal_bus.advance_detail_progress.emit(1)

        # 释放资源
        cap.release()
        out.release()

        self._signal_bus.set_detail_progress_finish.emit()
        return output_file_path

    def _audio_process(self, input_video_path: Path) -> Path:
        """
        读取输入视频，逐帧处理，然后写入输出视频,以及音频处理

        Args:
            input_video_path: 输入视频的路径
        """
        output_file_path = get_output_file_path(input_video_path, "audio_processed")
        self._audio_processor_manager.process(input_video_path)
        return output_file_path

    def _get_after_process_width_and_height(self, input_video_path: Path, ) -> tuple[int, int]:
        cap = cv2.VideoCapture(str(input_video_path))
        if not cap.isOpened():
            raise ValueError("无法打开输入视频")

        ret, frame = cap.read()
        if not ret:
            raise ValueError("无法读取视频的第一帧")
        processed_frame = self._video_processor_manager.process(frame)

        height, width = processed_frame.shape[:2]
        cap.release()
        return width, height

    def _set_running(self, is_running: bool):
        self.is_running = is_running

from pathlib import Path

import cv2
from moviepy.editor import VideoFileClip

from src.common.processors.base_processor import OpenCVProcessor


class VideoHandler:
    def process(self, input_video_path: Path,
                output_video_path: Path,
                processor: OpenCVProcessor):
        """
        读取输入视频，逐帧处理，然后写入输出视频,以及音频处理

        Args:
            input_video_path: 输入视频的路径
            output_video_path: 输出视频的路径
            processor: 用于处理视频的处理器
        """
        cap = cv2.VideoCapture(str(input_video_path))
        if not cap.isOpened():
            raise ValueError("无法打开输入视频")

        fps = cap.get(cv2.CAP_PROP_FPS)
        # 因为处理后的视频的宽高可能会发生变化，所以需要重新获取宽高
        width, height = self._get_after_process_width_and_height(input_video_path, processor)

        # MP4V比较通用，但是不支持透明度
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 对帧进行处理
            processed_frame = processor.process(frame)

            # 写入处理后的帧
            out.write(processed_frame)

        # 释放资源
        cap.release()
        out.release()

    def merge_videos(self, video_list: list[Path]):
        ...

    def compress_video(self, input_video_path: Path, output_video_path: Path):
        ...

    def _get_after_process_width_and_height(self,
                                            input_video_path: Path,
                                            processor: OpenCVProcessor) -> tuple[int, int]:
        cap = cv2.VideoCapture(str(input_video_path))
        if not cap.isOpened():
            raise ValueError("无法打开输入视频")

        ret, frame = cap.read()
        if not ret:
            raise ValueError("无法读取视频的第一帧")
        processed_frame = processor.process(frame)

        height, width = processed_frame.shape[:2]
        cap.release()
        return width, height

    def _replace_video_audio_A_with_B(self, video_path_A: Path, video_path_B: Path) -> Path:
        """
        将视频A的音频替换为视频B的音频
        """
        # Load video A and B
        video_a = VideoFileClip(str(video_path_A))
        video_b = VideoFileClip(str(video_path_B))

        audio_b = video_b.audio

        video_a_with_audio_b = video_a.set_audio(audio_b)

        output_video_path: Path = video_path_A.parent / f"{video_path_A.stem}_with_audio{video_path_A.suffix}"
        video_a_with_audio_b.write_videofile(str(output_video_path))

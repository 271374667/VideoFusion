import os
import time
from pathlib import Path
from typing import List, Literal

import cv2
import loguru
import numpy as np

from src.common.black_remover import BlackRemover
from src.common.ffmpeg_command import FFmpegCommand
from src.common.video_info import get_most_compatible_resolution, get_video_info
from src.core.datacls import VideoInfo
from src.core.enums import Orientation, Rotation
from src.core.paths import OUTPUT_FILE
from src.pipes import crop_video, resize_video, rotation_video
from src.signal_bus import SignalBus
from src.utils import evenly_distribute_numbers, evenly_interpolate_numbers


class VideoMosaic:
    def __init__(self):
        self._video_path_list: List[Path] = []
        self._output_file_path: Path = OUTPUT_FILE
        self._fps: int = 30
        self._best_width: int = 1280
        self._best_height: int = 720

        # 处理视频功能
        self._sample_rate: float = 0.5  # 该值表示从视频中采样的帧数占总帧数的比例
        self._video_orientation: Orientation = Orientation.VERTICAL
        self._horizontal_rotation: Rotation = Rotation.CLOCKWISE
        self._vertical_rotation: Rotation = Rotation.CLOCKWISE

        self._black_remover = BlackRemover()
        self._ffmpeg_command = FFmpegCommand()
        self._signal_bus = SignalBus()

    @property
    def video_path_list(self) -> List[Path]:
        return self._video_path_list

    @video_path_list.setter
    def video_path_list(self, video_path_list: List[Path]):
        self._video_path_list = [Path(x) for x in video_path_list]
        loguru.logger.debug(f'视频拼接:已添加{len(self._video_path_list)}个视频{self._video_path_list}')

    @property
    def output_file_path(self) -> Path:
        return self._output_file_path

    @output_file_path.setter
    def output_file_path(self, output_file_path: Path | str):
        self._output_file_path = Path(output_file_path)
        loguru.logger.debug(f'视频拼接:输出文件路径为{self._output_file_path}')

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, fps: int):
        if fps <= 0:
            raise ValueError('fps must be greater than 0')
        self._fps = fps
        loguru.logger.debug(f'视频拼接:输出视频帧率为{self._fps}')

    @property
    def sample_rate(self) -> float:
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sample_rate: float):
        if sample_rate > 1 or sample_rate < 0:
            raise ValueError('sample_rate must be between 0 and 1')
        self._sample_rate = sample_rate
        loguru.logger.debug(f'视频拼接:采样率为{self._sample_rate}')

    @property
    def video_orientation(self) -> Orientation:
        return self._video_orientation

    @video_orientation.setter
    def video_orientation(self, video_orientation: Orientation):
        self._video_orientation = video_orientation
        loguru.logger.debug(f'视频拼接:视频方向为{self._video_orientation}')

    @property
    def horizontal_rotation(self) -> Rotation:
        return self._horizontal_rotation

    @horizontal_rotation.setter
    def horizontal_rotation(self, horizontal_rotation: Rotation):
        self._horizontal_rotation = horizontal_rotation
        loguru.logger.debug(f'视频拼接:水平视频的旋转方向为{self._horizontal_rotation}')

    @property
    def vertical_rotation(self) -> Rotation:
        return self._vertical_rotation

    @vertical_rotation.setter
    def vertical_rotation(self, vertical_rotation: Rotation):
        self._vertical_rotation = vertical_rotation
        loguru.logger.debug(f'视频拼接:垂直视频的旋转方向为{self._vertical_rotation}')

    def add_video_dir(self, video_dir: Path | str, mode: str = '*.mp4') -> None:
        """添加视频文件夹"""
        if self._video_path_list:
            raise ValueError('video_path_list is not empty')
        video_dir = Path(video_dir)
        if not video_dir.is_dir():
            raise ValueError(f'{video_dir} is not a directory')
        video_path_list: List[Path] = list(video_dir.glob(mode))
        self.video_path_list = video_path_list

    def read_from_txt_file(self, txt_file: Path | str) -> None:
        """从txt文件中读取视频路径"""
        if self._video_path_list:
            raise ValueError('video_path_list is not empty')

        txt_file = Path(txt_file)
        if not txt_file.is_file():
            raise ValueError(f'{txt_file} is not a file')

        if not txt_file.exists():
            raise ValueError(f'{txt_file} does not exist')

        with open(txt_file, 'r', encoding='gbk') as f:
            video_path_list: List[Path] = [Path(x.strip()) for x in f.readlines()]
        self.video_path_list = video_path_list

    def start(self) -> None:
        start_time: float = time.time()
        video_info_list: List[VideoInfo] = get_video_info(self._video_path_list, self._video_orientation,
                                                          self._sample_rate)
        loguru.logger.info(f'视频拼接:获取视频信息完成,共计{len(video_info_list)}个视频:{video_info_list}')
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_max.emit(len(video_info_list))

        # 获取最佳分辨率
        loguru.logger.debug('视频拼接:正在获取最佳分辨率')
        best_width, best_height = get_most_compatible_resolution(video_info_list)
        self._best_width = best_width
        self._best_height = best_height
        loguru.logger.info(f'视频拼接:最佳分辨率为{self._best_width}x{self._best_height}')

        # 开始对视频依次执行[剪裁],[旋转],[缩放],[帧同步],[拼接]操作
        output_video = cv2.VideoWriter(str(self._output_file_path), cv2.VideoWriter.fourcc(*'mp4v'), self._fps,
                                       (self._best_width, self._best_height))
        for video_info in video_info_list:
            video = cv2.VideoCapture(str(video_info.video_path))
            fps: int = int(video.get(cv2.CAP_PROP_FPS))
            width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            total_seconds = total_frames / fps
            target_total_frames = int(total_seconds * self._fps)
            current_frame_index: int = 0

            # 设置进度条
            loguru.logger.debug(f'正在拼接视频[{video_info.video_path.name}]')
            loguru.logger.debug(f'当前视频时长为{total_seconds}s, 目标视频时长为{target_total_frames / self._fps}s')
            self._signal_bus.set_total_progress_description.emit('拼接视频')
            self._signal_bus.set_detail_progress_reset.emit()
            self._signal_bus.set_detail_progress_max.emit(total_frames)

            # 平滑抽帧或者平滑插值
            is_distribute: bool = fps > self._fps
            is_interpolate: bool = fps < self._fps
            frame_index_list: list[int] = []

            if is_distribute:
                frame_index_list = evenly_distribute_numbers(total_frames, target_total_frames)
                loguru.logger.warning(f'视频拼接:视频帧率为{fps}, 目标帧率为{self._fps}, 采用平滑抽帧')
            elif is_interpolate:
                frame_index_list = evenly_interpolate_numbers(total_frames, target_total_frames)
                loguru.logger.warning(f'视频拼接:视频帧率为{fps}, 目标帧率为{self._fps}, 采用平滑插帧')

            while True:
                # 如果当前的 fps 大于目标 fps, 则需要continue跳过一些帧
                if is_distribute and current_frame_index not in frame_index_list:
                    current_frame_index += 1
                    self._signal_bus.advance_detail_progress.emit(1)
                    continue

                ret, frame = video.read()
                if not ret:
                    break

                # 先对视频进行剪裁去黑边
                if self._is_video_need_crop(video_info):
                    frame = crop_video(frame, video_info.crop)

                # 对视频进行旋转
                if self._is_video_need_rotation(video_info):
                    # 如果是横屏视频, 且宽度大于高度, 则需要旋转
                    if self._video_orientation == Orientation.HORIZONTAL:
                        if self._horizontal_rotation == Rotation.NOTHING:
                            pass
                        elif self._horizontal_rotation == Rotation.CLOCKWISE:
                            frame = rotation_video(frame, 90)
                        elif self._horizontal_rotation == Rotation.COUNTERCLOCKWISE:
                            frame = rotation_video(frame, 270)
                        elif self._horizontal_rotation == Rotation.UPSIDE_DOWN:
                            frame = rotation_video(frame, 180)
                    # 如果是竖屏视频, 且宽度小于高度, 则需要旋转
                    elif self._video_orientation == Orientation.VERTICAL:
                        if self._vertical_rotation == Rotation.NOTHING:
                            pass
                        elif self._vertical_rotation == Rotation.CLOCKWISE:
                            frame = rotation_video(frame, 90)
                        elif self._vertical_rotation == Rotation.COUNTERCLOCKWISE:
                            frame = rotation_video(frame, 270)
                        elif self._vertical_rotation == Rotation.UPSIDE_DOWN:
                            frame = rotation_video(frame, 180)

                # 对视频进行缩放(如果视频的分辨率不是最佳分辨率)
                if width != self._best_width or height != self._best_height:
                    frame = resize_video(frame, self._best_width, self._best_height)

                # 如果当前的 fps 小于目标 fps, 则需要重复一些帧
                if is_interpolate:
                    repeat_time: int = frame_index_list.count(current_frame_index)
                    for _ in range(repeat_time):
                        output_video.write(frame)
                # 不需要补帧或者抽帧
                else:
                    output_video.write(frame)

                current_frame_index += 1
                self._signal_bus.advance_detail_progress.emit(1)
            self._signal_bus.advance_total_progress.emit(1)
            video.release()
            loguru.logger.debug(f'视频拼接:完成一个视频: {video_info.video_path.name}')
        output_video.release()
        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        # 开始拼接音频
        loguru.logger.info('视频拼接完成,开始拼接音频')
        # 在目标视频的目录下创建一个临时文件夹
        audio_output_file: Path = self._output_file_path.parent / 'audio.mp3'

        extracted_audios: List[Path] = [x.video_path for x in video_info_list]
        audio_file_path = self._ffmpeg_command.audio_extract(extracted_audios,
                                                             audio_output_file)
        # 合并视频和音频
        self._ffmpeg_command.merge_video_with_audio(self._output_file_path, audio_file_path)

        # 压缩视频
        compress_video_path: Path = self._output_file_path.parent / "压缩.mp4"
        self._ffmpeg_command.compress_video(self._output_file_path, compress_video_path)

        loguru.logger.info(
                f'\n视频拼接:视频拼接完成, 输出文件为[{self._output_file_path}], 总共耗时[{time.time() - start_time:.2f}s]\n')
        self._signal_bus.finished.emit()
        # 打开输出文件的目录
        os.startfile(self._output_file_path.parent)

    def _is_video_need_crop(self, video_info: VideoInfo) -> bool:
        return video_info.crop is not None

    def _is_video_need_rotation(self, video_info: VideoInfo) -> bool:
        """视频是否需要旋转, 横屏视频宽度大于高度, 竖屏视频宽度小于高度"""
        return (
                self._video_orientation != Orientation.HORIZONTAL
                or video_info.width <= video_info.height
        ) and (
                self._video_orientation != Orientation.VERTICAL
                or video_info.width >= video_info.height
        )

    def _rotation_video(self, frame: np.ndarray, angle: Literal[90, 180, 270]) -> np.ndarray:
        match angle:
            case 90:
                return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            case 180:
                return cv2.rotate(frame, cv2.ROTATE_180)
            case 270:
                return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            case _:
                raise ValueError('angle must be 90, 180 or 270')

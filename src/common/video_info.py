import random
from collections import Counter
from pathlib import Path
from typing import Tuple

import cv2
import loguru

from src.common.black_remove.img_black_remover import BlackRemover
from src.common.black_remove.video_remover import VideoRemover
from src.core.datacls import CropInfo, VideoInfo
from src.core.enums import Orientation
from src.signal_bus import SignalBus

black_remover = BlackRemover()
video_remover = VideoRemover()
signal_bus = SignalBus()


def _img_black_remover_start(video_path: Path, sample_rate: float) -> VideoInfo:
    # 重新获取视频信息
    video = cv2.VideoCapture(str(video_path))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width: int = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height: int = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    # 如果有黑边则需要获取主体区域坐标(只获取部分百比分帧)
    sample_frames = int(total_frames * sample_rate)
    # 计算每次需要跳过的帧数
    skip_frames = total_frames // sample_frames if sample_frames else 0

    coordinates = []
    if skip_frames <= 0:
        skip_frames = 1
    for i in range(0, total_frames, skip_frames):
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = video.read()

        # 获取进度条增加的数量
        signal_bus.set_detail_progress_current.emit(i)
        if not ret:
            break
        # Use BlackRemover to get the coordinates of the frame without black borders
        coordinates.append(black_remover.start(img_array=frame))

    signal_bus.set_detail_progress_finish.emit()
    signal_bus.advance_total_progress.emit(1)
    video.release()

    # Get the most common coordinates
    most_common_coordinates = Counter(coordinates).most_common(1)[0][0]

    # 把坐标转化成x, y, w, h
    most_common_coordinates = (
            most_common_coordinates[0],
            most_common_coordinates[1],
            most_common_coordinates[2] - most_common_coordinates[0],
            most_common_coordinates[3] - most_common_coordinates[1]
            )

    x, y, w, h = most_common_coordinates
    x = max(0, x)
    y = max(0, y)
    w = min(width, w)
    h = min(height, h)

    # 如果剪裁区域的宽高和原视频的宽高相同则不剪裁
    if w == width and h == height:
        return VideoInfo(video_path, fps, total_frames, width, height, None)

    loguru.logger.debug(f'[{video_path.name}]的主体区域坐标为{x, y, w, h}')
    signal_bus.set_total_progress_finish.emit()
    signal_bus.set_detail_progress_finish.emit()
    return VideoInfo(video_path, fps, total_frames, width, height, CropInfo(*most_common_coordinates))


def _video_black_remover_start(video_path: Path) -> VideoInfo:
    video = cv2.VideoCapture(str(video_path))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 获取结果
    x, y, w, h = video_remover.start(video_path)

    if w == width and h == height:
        return VideoInfo(video_path, fps, total_frames, width, height, None)
    return VideoInfo(video_path, fps, total_frames, width, height, CropInfo(x, y, w, h))


def get_video_info(video_path: Path, sample_rate: float = 0.5) -> VideoInfo:
    video = cv2.VideoCapture(str(video_path))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    loguru.logger.debug(f'正在获取视频信息[{video_path.name}]')
    signal_bus.set_detail_progress_reset.emit()
    signal_bus.set_detail_progress_max.emit(total_frames)

    if sample_rate == 0:
        return VideoInfo(video_path, fps, total_frames, width, height, None)

    # 先判断是否有黑边(获取视频中随机的10帧)
    random_frames = random.sample(range(total_frames), 10)
    is_black = False
    for i in random_frames:
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = video.read()
        if not ret:
            break
        if black_remover.has_black_border(frame):
            is_black = True
            break
    if not is_black:
        return VideoInfo(video_path, fps, total_frames, width, height, None)
    video.release()

    if sample_rate != 1:
        return _img_black_remover_start(video_path, sample_rate)
    else:
        return _video_black_remover_start(video_path)


def get_most_compatible_resolution(video_info_list: list[VideoInfo],
                                   orientation: Orientation = Orientation.VERTICAL) -> Tuple[int, int]:
    """获取最合适的视频分辨率"""
    resolutions: list[Tuple[int, int]] = []
    for each in video_info_list:
        width, height = (each.crop.w, each.crop.h) if each.crop else (each.width, each.height)
        # 判断视频的方向,如果视频的方向和用户选择的方向不一致则需要调换宽高
        if (orientation == Orientation.HORIZONTAL and width > height) or (
                orientation == Orientation.VERTICAL and width < height):
            resolutions.append((width, height))
        else:
            resolutions.append((height, width))

    aspect_ratios: list[float] = [i[0] / i[1] for i in resolutions]
    most_common_ratio = Counter(aspect_ratios).most_common(1)[0][0]
    compatible_resolutions = [res for res in resolutions if (res[0] / res[1]) == most_common_ratio]
    compatible_resolutions.sort(key=lambda x: (x[0] * x[1]), reverse=True)
    width, height = compatible_resolutions[0][:2]
    return width, height


if __name__ == '__main__':
    print(get_video_info(Path(r"E:\load\python\Project\VideoFusion\测试\dy\b7bb97e21600b07f66c21e7932cb7550.mp4"), 0.5))

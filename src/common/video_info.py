import random
from collections import Counter
from pathlib import Path
from typing import List, Tuple

import cv2
import loguru

from src.common.black_remover import BlackRemover
from src.core.datacls import CropInfo, VideoInfo
from src.core.enums import Orientation
from src.signal_bus import SignalBus

black_remover = BlackRemover()
signal_bus = SignalBus()


def get_video_info(video_path_list: List[Path], orientation: Orientation, sample_rate: float = 0.5) -> List[VideoInfo]:
    video_info_list: List[VideoInfo] = []
    signal_bus.set_total_progress_reset.emit()
    signal_bus.set_detail_progress_reset.emit()
    signal_bus.set_total_progress_max.emit(len(video_path_list))
    signal_bus.set_total_progress_description.emit('收集信息')
    for video_path in video_path_list:
        video = cv2.VideoCapture(str(video_path))
        fps = int(video.get(cv2.CAP_PROP_FPS))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        loguru.logger.debug(f'正在获取视频信息[{video_path.name}]')
        signal_bus.set_detail_progress_reset.emit()
        signal_bus.set_detail_progress_max.emit(total_frames)

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
            signal_bus.advance_total_progress.emit(1)
            video_info_list.append(VideoInfo(video_path, fps, total_frames, width, height))
            continue

        # 如果有黑边则需要获取主体区域坐标(只获取部分百比分帧)
        sample_frames = int(total_frames * sample_rate)
        # 计算每次需要跳过的帧数
        skip_frames = total_frames // sample_frames if sample_frames else 0

        coordinates = []
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

        # 如果视频是横向的，且宽度小于高度，或者视频是纵向的，且宽度大于高度，则交换宽高
        if ((orientation == Orientation.HORIZONTAL and w < h)
                or (orientation == Orientation.VERTICAL and w > h)):
            most_common_coordinates = (x, y, h, w)
        video_info_list.append(
                VideoInfo(video_path, fps, total_frames, width, height, CropInfo(*most_common_coordinates)))
        loguru.logger.debug(f'[{video_path.name}]的主体区域坐标为{x, y, w, h}')
    signal_bus.set_total_progress_finish.emit()
    signal_bus.set_detail_progress_finish.emit()
    return video_info_list


def get_most_compatible_resolution(video_info_list: list[VideoInfo]) -> Tuple[int, int]:
    """获取最合适的视频分辨率"""
    resolutions: list[Tuple[int, int]] = []
    for each in video_info_list:
        if each.crop:
            resolutions.append((each.crop.w, each.crop.h))
            continue
        resolutions.append((each.width, each.height))

    aspect_ratios: list[float] = [i[0] / i[1] for i in resolutions]
    most_common_ratio = Counter(aspect_ratios).most_common(1)[0][0]
    compatible_resolutions = [res for res in resolutions if (res[0] / res[1]) == most_common_ratio]
    compatible_resolutions.sort(key=lambda x: (x[0] * x[1]), reverse=True)
    width, height = compatible_resolutions[0][:2]
    return width, height


if __name__ == '__main__':
    get_video_info([Path(r"E:\load\python\Project\VideoMosaic\temp\001.mp4")], Orientation.HORIZONTAL, 0.5)

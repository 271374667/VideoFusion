from collections import Counter
from pathlib import Path

import cv2
import loguru
import numpy as np

from src.common.black_remove_algorithm.black_remove_algorithm import BlackRemoveAlgorithm
from src.common.utils.image_utils import ImageUtils
from src.signal_bus import SignalBus

signal_bus = SignalBus()


class IMGBlackRemover(BlackRemoveAlgorithm):
    def __init__(self, threshold: int = 30, border_width: int = 5):
        self.threshold: int = threshold
        self.border_width: int = border_width

        self._image_utils = ImageUtils()

    def remove_black(self, input_file_path: str | Path, max_frames: int = 500) -> tuple[int, int, int, int]:
        input_file_path: Path = Path(input_file_path)
        # 如果不是视频则报错
        if input_file_path.suffix not in ['.mp4', '.avi', '.flv', '.mov', '.mkv']:
            raise ValueError(f"文件不是视频: {input_file_path}")

        # 如果不存在则报错
        if not input_file_path.exists():
            raise FileNotFoundError(f"文件不存在: {input_file_path}")

        video = cv2.VideoCapture(str(input_file_path))
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        width: int = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height: int = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 如果有黑边则需要获取主体区域坐标(只获取部分百比分帧)
        sample_frames = int(total_frames * 0.5)
        # 限制最大采样帧数,不然长时间的视频会导致等待时间过长
        sample_frames = min([max_frames, sample_frames])
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
            coordinates.append(self._analyze_each_frame(frame))

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

        loguru.logger.debug(f'[{input_file_path.name}]的主体区域坐标为{x, y, w, h}')
        signal_bus.set_total_progress_finish.emit()
        signal_bus.set_detail_progress_finish.emit()
        return x, y, w, h

    def _analyze_each_frame(self, frame: np.ndarray) -> tuple[int, int, int, int]:
        # 获取图片的长和宽
        img_height: int = frame.shape[0]
        img_width: int = frame.shape[1]
        # 图片裁剪的左上角和右下角坐标
        left_top_x: int = 0
        left_top_y: int = 0
        right_bottom_x: int = img_width
        right_bottom_y: int = img_height

        # 如果图像有黑边，则直接返回
        if not self._image_utils.has_black_border(frame):
            # loguru.logger.debug(f'{img_path} dont have black border, skip it')
            return left_top_x, left_top_y, right_bottom_x, right_bottom_y

        # 转换为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 计算平均亮度阈值
        # mean_threshold = np.mean(gray)

        # _, binary = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((5, 5), np.uint8)

        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # 找出图像中的连通区域
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)

        # 创建一个新的二值图像，用于保存去除孤立区域后的结果
        new_binary = np.zeros_like(binary)

        # 遍历所有连通区域
        for i in range(1, num_labels):
            # 如果该连通区域的大小大于阈值，则保留该区域
            if stats[i, cv2.CC_STAT_AREA] > 1500:  # 500是阈值，可以根据实际情况调整
                new_binary[labels == i] = 255

        # 找出图像中的轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 找出最大的矩形轮廓
        max_area = 0
        max_rect = None
        for contour in contours:
            rect = cv2.boundingRect(contour)
            x, y, w, h = rect
            area = w * h
            if area > max_area:
                max_area = area
                max_rect = rect

        # 在原图像上画出该矩形轮廓
        if max_rect is not None:
            x, y, w, h = max_rect
            left_top_x = x
            left_top_y = y
            right_bottom_x = x + w
            right_bottom_y = y + h

        # # 绘图显示
        # cv2.rectangle(img, (left_top_x, left_top_y), (right_bottom_x, right_bottom_y), (0, 0, 255), 15)
        # # 保持横纵比的情况下将图片缩放到720p
        # img = cv2.resize(img, (480, 720))
        # cv2.imshow('new_binary', new_binary)
        # cv2.imshow('img', img)
        # # cv2.imwrite(r"E:\load\python\Project\VideoMosaic\temp\dy\temp.png", img)
        # cv2.waitKey(0)
        return left_top_x, left_top_y, right_bottom_x, right_bottom_y


if __name__ == '__main__':
    b = IMGBlackRemover()
    img = r"E:\load\python\Project\VideoFusion\tests\test_data\videos\001.mp4"
    print(b.remove_black(img))

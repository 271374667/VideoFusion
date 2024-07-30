from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np


class BlackRemover:
    def __init__(self, threshold: int = 30, border_width: int = 5):
        self.threshold: int = threshold
        self.border_width: int = border_width

    def start(self, img_path: Optional[Union[str, Path]] = None,
              img_array: Optional[np.ndarray] = None) -> tuple[int, int, int, int]:
        """
        去除图像黑边,可以传入图像路径或者图像数组

        Args:
            img_path: 图像路径
            img_array: 图像数组

        Returns:
            tuple[int, int, int, int]: 左上角和右下角坐标
        """
        if img_path is None and img_array is None:
            raise ValueError('img_path and img_array cannot be None at the same time')
        elif img_path is not None and img_array is not None:
            raise ValueError('img_path and img_array cannot be set at the same time')
        elif img_path is not None:
            if isinstance(img_path, Path):
                img_path = str(img_path)
            # 读取图像
            img = cv2.imread(img_path)
        else:
            img = img_array
        # 获取图片的长和宽
        img_height: int = img.shape[0]
        img_width: int = img.shape[1]
        # 图片裁剪的左上角和右下角坐标
        left_top_x: int = 0
        left_top_y: int = 0
        right_bottom_x: int = img_width
        right_bottom_y: int = img_height

        # 如果图像有黑边，则直接返回
        if not self.has_black_border(img):
            # loguru.logger.debug(f'{img_path} dont have black border, skip it')
            return left_top_x, left_top_y, right_bottom_x, right_bottom_y

        # 转换为灰度图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 计算平均亮度阈值
        # mean_threshold = np.mean(gray)

        _, binary = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
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

    def has_black_border(self, img: np.ndarray) -> bool:
        """
        判断图像是否有黑边

        Args:
            img: 图像

        Returns:
            bool: 是否有黑边
        """
        # 读取图像
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        threshold = self.threshold
        border_width = self.border_width

        # 检查上下左右四个边缘的像素值
        top_edge = img[:border_width, :]
        bottom_edge = img[-border_width:, :]
        left_edge = img[:, :border_width]
        right_edge = img[:, -border_width:]

        # 如果这些像素值的平均值都小于给定的阈值（默认为50），那么函数返回True，表示图像有黑边
        if np.mean(top_edge) < threshold or np.mean(bottom_edge) < threshold or np.mean(
                left_edge) < threshold or np.mean(right_edge) < threshold:
            return True
        else:
            return False

    def is_black(self, img: np.ndarray) -> bool:
        """
        判断图像是否为黑色

        Args:
            img: 图像

        Returns:
            bool: 是否为黑色
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        threshold = self.threshold
        return np.mean(img) < threshold


if __name__ == '__main__':
    b = BlackRemover()
    img = r"E:\load\python\Project\VideoFusion\TempAndTest\dy\Clip_2024-06-03_15-23-02.png"
    b.start(img_path=img)

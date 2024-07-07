from pathlib import Path

import cv2
import numpy as np

img_suffix: list[str] = ['.png', '.jpg', '.jpeg', '.bmp', '.webp', '.svg']


class ImageUtils:
    def __init__(self, threshold: int = 30, border_width: int = 5):
        self.threshold: int = threshold
        self.border_width: int = border_width

    def read_image(self, img_path: str | Path) -> np.ndarray:
        """
        读取图像

        Args:
            img_path: 图像路径

        Returns:
            np.ndarray: 图像数组
        """
        if not Path(img_path).exists():
            raise FileNotFoundError(f"文件不存在: {img_path}")

        if Path(img_path).suffix not in img_suffix:
            raise ValueError(f"不支持的文件格式: {img_path}")
        return cv2.imread(str(img_path))

    def is_black(self, img: np.ndarray) -> bool:
        """
        判断图像是否为黑色

        Args:
            img: 图像

        Returns:
            bool: 是否为黑色
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return np.mean(img) < self.threshold

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
        return (
                np.mean(top_edge) < threshold
                or np.mean(bottom_edge) < threshold
                or np.mean(left_edge) < threshold
                or np.mean(right_edge) < threshold
        )

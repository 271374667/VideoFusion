import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor


class DeblockProcessor(OpenCVProcessor):
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        使用cv2.medianBlur对输入的帧进行去色块处理

        Args:
            frame: 输入的帧

        Returns:
            去色块处理后的帧
        """
        # 使用中值滤波去色块，这里的5是滤波器的大小
        return cv2.medianBlur(frame, 5)

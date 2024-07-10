import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor


class BilateralDenoiseProcessor(OpenCVProcessor):
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        使用cv2.bilateralFilter对输入的帧进行降噪处理

        Args:
            frame: 输入的帧，一个numpy数组

        Returns:
            处理后的帧，一个numpy数组
        """
        return cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)

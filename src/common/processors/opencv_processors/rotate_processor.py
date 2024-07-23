import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.core.enums import Orientation


class RotateProcessor(OpenCVProcessor):
    def __init__(self):
        self._processor_global_var = ProcessorGlobalVar()
        # 获取旋转的角度{0, 90, 180, 270}

    def process(self, frame: np.ndarray) -> np.ndarray:
        angle: int = self._processor_global_var.get('rotation_angle')
        orientation: Orientation = self._processor_global_var.get("orientation")

        if orientation is None:
            raise ValueError("orientation is required")

        if angle is None:
            raise ValueError("angle is required")

        # 将角度转换为OpenCV的旋转角度
        match angle:
            case 0:
                cv2_angle = cv2.ROTATE_90_CLOCKWISE
            case 90:
                cv2_angle = cv2.ROTATE_90_COUNTERCLOCKWISE
            case 180:
                cv2_angle = cv2.ROTATE_180
            case 270:
                cv2_angle = cv2.ROTATE_90_CLOCKWISE
            case _:
                raise ValueError(f"Invalid angle: {angle}")

        frame_width: int = frame.shape[1]
        frame_height: int = frame.shape[0]

        # 如果视频的宽高和视频的朝向不一致，则旋转视频
        # 例如视频的宽300，高100，此时视频是一个横屏视频，但是视频的朝向是竖屏,此时就要旋转
        # 视频的宽高和视频的朝向一致，则不需要旋转
        if (((orientation == Orientation.HORIZONTAL) and (frame_height > frame_width))
                or (orientation == Orientation.VERTICAL and frame_width > frame_height)):
            frame = cv2.rotate(frame, cv2_angle)
        return frame

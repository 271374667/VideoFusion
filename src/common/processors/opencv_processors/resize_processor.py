import cv2
import loguru
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.config import ScalingQuality, cfg


class ResizeCache:
    def __init__(self):
        self.new_width = None
        self.new_height = None
        self.pad_top = None
        self.pad_bottom = None
        self.pad_left = None
        self.pad_right = None

    def is_set(self):
        return all([self.new_width, self.new_height, self.pad_top, self.pad_bottom, self.pad_left, self.pad_right])

    def set_values(self, new_width, new_height, pad_top, pad_bottom, pad_left, pad_right):
        self.new_width = new_width
        self.new_height = new_height
        self.pad_top = pad_top
        self.pad_bottom = pad_bottom
        self.pad_left = pad_left
        self.pad_right = pad_right

    def reset(self):
        self.__init__()


class ResizeProcessor(OpenCVProcessor):
    def __init__(self):
        self._processor_global_var = ProcessorGlobalVar()
        self._cache = ResizeCache()

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        调整输入帧的大小，使其尽可能接近指定分辨率，剩余部分使用黑边填充。

        Args:
            frame: 输入的帧，一个numpy数组

        Returns:
            处理后的帧，一个numpy数组
        """
        # 不需要合并就不需要调整分辨率
        is_merge: bool = cfg.get(cfg.merge_video)
        if not is_merge:
            return frame

        target_width: int = self._processor_global_var.get("target_width")
        target_height: int = self._processor_global_var.get("target_height")
        # 获取输入帧的宽度和高度
        height, width = frame.shape[:2]

        # 检查是否有缓存
        if not self._cache.is_set():
            new_width, new_height, pad_top, pad_bottom, pad_left, pad_right = self._calculate_dimensions(width, height,
                                                                                                         target_width,
                                                                                                         target_height)
            self._cache.set_values(new_width, new_height, pad_top, pad_bottom, pad_left, pad_right)
        else:
            new_width = self._cache.new_width
            new_height = self._cache.new_height
            pad_top = self._cache.pad_top
            pad_bottom = self._cache.pad_bottom
            pad_left = self._cache.pad_left
            pad_right = self._cache.pad_right

        # 缩放视频帧到新的尺寸
        resize_algorithm: ScalingQuality = cfg.get(cfg.scaling_quality)
        match resize_algorithm:
            case ScalingQuality.NEAREST:
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
            case ScalingQuality.BILINEAR:
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            case ScalingQuality.BICUBIC:
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            case ScalingQuality.LANCZOS:
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            case ScalingQuality.SINC:
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            case _:
                loguru.logger.error(f"Invalid scaling quality: {resize_algorithm}")
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        return cv2.copyMakeBorder(
                resized_frame,
                pad_top,
                pad_bottom,
                pad_left,
                pad_right,
                cv2.BORDER_CONSTANT,
                value=[0, 0, 0],
                )

    def _calculate_dimensions(self, width: int, height: int, target_width: int, target_height: int):
        if width == 0 or height == 0:
            loguru.logger.critical("视频的宽度或高度为0, 请检查视频")
            raise ValueError("Width or height is 0")
        scale = min(target_width / width, target_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        pad_top = (target_height - new_height) // 2
        pad_bottom = target_height - new_height - pad_top
        pad_left = (target_width - new_width) // 2
        pad_right = target_width - new_width - pad_left
        return new_width, new_height, pad_top, pad_bottom, pad_left, pad_right

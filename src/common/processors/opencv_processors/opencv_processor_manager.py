import numpy as np

from src.common.processors.base_processor import BaseProcessorManager, OpenCVProcessor, T
from src.common.processors.opencv_processors.bilateral_denoise_processor import BilateralDenoiseProcessor
from src.common.processors.opencv_processors.brightness_contrast_processor import BrightnessContrastProcessor
from src.common.processors.opencv_processors.crop_processor import CropProcessor
from src.common.processors.opencv_processors.deband_processor import DebandProcessor
from src.common.processors.opencv_processors.deblock_processor import DeblockProcessor
from src.common.processors.opencv_processors.means_denoise_processor import MeansDenoiseProcessor
from src.common.processors.opencv_processors.resize_processor import ResizeProcessor
from src.common.processors.opencv_processors.rotate_processor import RotateProcessor
from src.common.processors.opencv_processors.super_resolution_processor import (SuperResolutionESPCNProcessor,
                                                                                SuperResolutionLapSRNProcessor)
from src.common.processors.opencv_processors.white_balance_processor import WhiteBalanceProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.config import SuperResolutionAlgorithm, VideoNoiseReduction, cfg


class OpenCVProcessorManager(BaseProcessorManager[np.ndarray]):
    def __init__(self):
        super().__init__()
        self._processor_global_var = ProcessorGlobalVar()
        self._crop_processor = CropProcessor()
        self._rotate_processor = RotateProcessor()
        self._resize_processor = ResizeProcessor()
        self._white_balance_processor = WhiteBalanceProcessor()
        self._brightness_contrast_processor = BrightnessContrastProcessor()
        self._means_denoise_processor = MeansDenoiseProcessor()
        self._bilateral_denoise_processor = BilateralDenoiseProcessor()
        self._deband_processor = DebandProcessor()
        self._deblock_processor = DeblockProcessor()
        self._super_resolution_espcn_processor = SuperResolutionESPCNProcessor()
        self._super_resolution_lapsrn_processor = SuperResolutionLapSRNProcessor()

        self._processors: list[OpenCVProcessor] = [
                self._crop_processor,
                self._rotate_processor,
                self._resize_processor,
                self._white_balance_processor,
                self._brightness_contrast_processor,
                self._means_denoise_processor,
                self._bilateral_denoise_processor,
                self._deband_processor,
                self._deblock_processor,
                self._super_resolution_espcn_processor,
                self._super_resolution_lapsrn_processor]

    def get_processors(self) -> list[OpenCVProcessor]:
        return self._processors

    def get_crop_processor(self) -> CropProcessor:
        return self._crop_processor

    def add_processor(self, processor: OpenCVProcessor):
        self._processors.append(processor)

    def process(self, x: T) -> T:
        # 有哪一些处理器是启用的
        self._check_enabled_processors()

        for processor in self._processors:
            if not processor.is_enable:
                continue
            x = processor.process(x)
        return x

    def _check_enabled_processors(self):
        """读取配置文件，判断哪些处理器是启用的
        """
        # 白平衡
        self._white_balance_processor.is_enable = cfg.get(cfg.white_balance)
        # 亮度对比度
        self._brightness_contrast_processor.is_enable = cfg.get(cfg.brightness_contrast)

        # 视频降噪
        denoise_value: VideoNoiseReduction = cfg.get(cfg.video_noise_reduction)
        match denoise_value:
            case VideoNoiseReduction.Disable:
                self._means_denoise_processor.is_enable = False
                self._bilateral_denoise_processor.is_enable = False
            case VideoNoiseReduction.Nlmeans:
                self._means_denoise_processor.is_enable = True
                self._bilateral_denoise_processor.is_enable = False
            case VideoNoiseReduction.Bilateral:
                self._means_denoise_processor.is_enable = False
                self._bilateral_denoise_processor.is_enable = True
            case _:
                raise ValueError("未知的视频降噪算法")

        # 去色带
        self._deband_processor.is_enable = cfg.get(cfg.deband)
        # 去色块
        self._deblock_processor.is_enable = cfg.get(cfg.deblock)
        # 超分辨率
        super_resolution_value = cfg.get(cfg.super_resolution_algorithm)
        match super_resolution_value:
            case SuperResolutionAlgorithm.ESPCN:
                self._super_resolution_espcn_processor.is_enable = True
                self._super_resolution_lapsrn_processor.is_enable = False
            case SuperResolutionAlgorithm.LAPSRN:
                self._super_resolution_espcn_processor.is_enable = False
                self._super_resolution_lapsrn_processor.is_enable = True
            case SuperResolutionAlgorithm.Disable:
                self._super_resolution_espcn_processor.is_enable = False
                self._super_resolution_lapsrn_processor.is_enable = False
            case _:
                raise ValueError("未知的超分辨率算法")


if __name__ == '__main__':
    import cv2
    from src.core.enums import Orientation

    input_video_file_path = r"E:\load\python\Project\VideoFusion\TempAndTest\dy\b7bb97e21600b07f66c21e7932cb7550.mp4"
    m = OpenCVProcessorManager()
    global_var = ProcessorGlobalVar()

    global_var.update("crop_x", 0)
    global_var.update("crop_y", 515)
    global_var.update("crop_width", 716)
    global_var.update("crop_height", 482)
    global_var.update("rotation_angle", 90)
    global_var.update("orientation", Orientation.HORIZONTAL)
    global_var.update("target_width", 500)
    global_var.update("target_height", 300)
    # 读取视频
    cap = cv2.VideoCapture(input_video_file_path)
    if not cap.isOpened():
        raise ValueError("无法打开输入视频")

    # 读取第一帧
    ret, frame = cap.read()
    if not ret:
        raise ValueError("无法读取视频帧")

    # 处理第一帧
    processed_frame = m.process(frame)

    # 展示处理后的帧
    cv2.imshow('Processed Frame', processed_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 释放视频捕获对象
    cap.release()

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


class OpenCVProcessorManager(BaseProcessorManager[np.ndarray]):
    def __init__(self):
        super().__init__()
        self._processors: list[OpenCVProcessor] = []
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

    def get_processors(self) -> list[OpenCVProcessor]:
        return self._processors

    def add_processor(self, processor: OpenCVProcessor):
        self._processors.append(processor)

    def process(self, x: T) -> T:
        for processor in self._processors:
            if not processor.is_enable:
                continue
            x = processor.process(x)
        return x

    def _pre_process(self):
        self._processors = [self._crop_processor,
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

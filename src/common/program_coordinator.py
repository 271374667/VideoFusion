from src.common.processors.opencv_processors.bilateral_denoise_processor import BilateralDenoiseProcessor
from src.common.processors.opencv_processors.means_denoise_processor import MeansDenoiseProcessor
from src.common.processors.opencv_processors.opencv_processor_manager import OpenCVProcessorManager


class ProgramCoordinator:
    def __init__(self):
        self._opencv_processor_manager = OpenCVProcessorManager()
        self._opencv_processor_manager.add_processor(BilateralDenoiseProcessor())
        self._opencv_processor_manager.add_processor(MeansDenoiseProcessor())

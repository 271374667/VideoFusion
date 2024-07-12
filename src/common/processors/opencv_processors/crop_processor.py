import numpy as np

from src.common.processors.base_processor import OpenCVProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar


class CropProcessor(OpenCVProcessor):
    def __init__(self):
        self.processor_global_var = ProcessorGlobalVar()
        self.crop_x: int = self.processor_global_var.get("crop_x")
        self.crop_y: int = self.processor_global_var.get("crop_y")
        self.crop_width: int = self.processor_global_var.get("crop_width")
        self.crop_height: int = self.processor_global_var.get("crop_height")

    def process(self, frame: np.ndarray) -> np.ndarray:
        # 如果其中一个参数为None，则不进行裁剪
        if self.crop_x is None or self.crop_y is None or self.crop_width is None or self.crop_height is None:
            return frame

        return frame[self.crop_y:self.crop_y + self.crop_height, self.crop_x:self.crop_x + self.crop_width]

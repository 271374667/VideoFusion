import numpy as np

from src.common.processors.base_processor import OpenCVProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar


class CropProcessor(OpenCVProcessor):
    def __init__(self):
        self.processor_global_var = ProcessorGlobalVar()

    def process(self, frame: np.ndarray) -> np.ndarray:
        crop_x: int = self.processor_global_var.get("crop_x")
        crop_y: int = self.processor_global_var.get("crop_y")
        crop_width: int = self.processor_global_var.get("crop_width")
        crop_height: int = self.processor_global_var.get("crop_height")

        # 如果全部都为None，则不进行裁剪
        if crop_x is None and crop_y is None and crop_width is None and crop_height is None:
            return frame

        # 如果只有一个参数为None对那个参数进行报错
        if crop_x is None:
            raise ValueError("crop_x 为None")
        elif crop_y is None:
            raise ValueError("crop_y 为None")
        elif crop_width is None:
            raise ValueError("crop_width 为None")
        elif crop_height is None:
            raise ValueError("crop_height 为None")

        return frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]

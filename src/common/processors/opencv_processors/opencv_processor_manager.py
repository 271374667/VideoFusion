
import numpy as np

from src.common.processors.base_processor import BaseProcessorManager, OpenCVProcessor, T


class OpenCVProcessorManager(BaseProcessorManager[np.ndarray]):
    def __init__(self):
        super().__init__()
        self._processors: list[OpenCVProcessor] = []

    def get_processors(self) -> list[OpenCVProcessor]:
        return self._processors

    def add_processor(self, processor: OpenCVProcessor):
        self._processors.append(processor)

    def process(self, x: T) -> T:
        for processor in self._processors:
            x = processor.process(x)
        return x

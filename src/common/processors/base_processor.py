from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import numpy as np

from src.core.datacls import FFmpegDTO

T = TypeVar("T")


class BaseProcessor(ABC, Generic[T]):
    @abstractmethod
    def process(self, x: T) -> T:
        pass


class OpenCVProcessor(BaseProcessor):
    is_enable: bool = True

    @abstractmethod
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        将输入的帧进行处理并返回处理后的帧

        Args:
            frame: 输入的帧

        Returns:
            处理后的帧
        """
        raise NotImplementedError("Not implemented yet")


class FFmpegProcessor(BaseProcessor):
    @abstractmethod
    def process(self, ffmpeg_dto: list[FFmpegDTO]) -> list[FFmpegDTO]:
        """
        将输入的文件进行处理并返回处理后的文件路径

        Args:
            ffmpeg_dto: 输入文件路径

        Returns:
            处理后的文件路径
        """
        raise NotImplementedError("Not implemented yet")


class EXEProcessor(BaseProcessor):
    @abstractmethod
    def process(self, input_file_path: Path) -> Path:
        """
        将输入的文件进行处理并返回处理后的文件路径

        Args:
            input_file_path: 输入文件路径

        Returns:
            处理后的文件路径
        """
        raise NotImplementedError("Not implemented yet")


class BaseProcessorManager(ABC, Generic[T]):
    def __init__(self):
        self._processors: list[BaseProcessor] = []

    def get_processors(self) -> list[BaseProcessor]:
        return self._processors

    def add_processor(self, processor: BaseProcessor):
        self._processors.append(processor)

    def process(self, x: T) -> T:
        for processor in self._processors:
            x = processor.process(x)
        return x


class FFmpegProcessorManager(BaseProcessorManager[FFmpegDTO]):
    def __init__(self):
        super().__init__()
        self._processors: list[FFmpegProcessor] = []

    def get_processors(self) -> list[FFmpegProcessor]:
        return self._processors

    def add_processor(self, processor: FFmpegProcessor):
        self._processors.append(processor)

    def process(self, x: T) -> T:
        for processor in self._processors:
            x = processor.process(x)
        return x


class EXEProcessorManager(BaseProcessorManager[Path]):
    def __init__(self):
        super().__init__()
        self._processors: list[EXEProcessor] = []

    def get_processors(self) -> list[EXEProcessor]:
        return self._processors

    def add_processor(self, processor: EXEProcessor):
        self._processors.append(processor)

    def process(self, x: T) -> T:
        for processor in self._processors:
            x = processor.process(x)
        return x

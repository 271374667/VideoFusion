from abc import ABC, abstractmethod
from pathlib import Path


class BaseVideoEngine(ABC):
    @abstractmethod
    def process_video(self, input_video_path: Path) -> Path:
        raise NotImplementedError("This method must be implemented by subclass")

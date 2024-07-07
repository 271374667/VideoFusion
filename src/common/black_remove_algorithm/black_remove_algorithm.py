from abc import ABC, abstractmethod
from pathlib import Path


class BlackRemoveAlgorithm(ABC):
    @abstractmethod
    def remove_black(self, input_file_path: str | Path) -> tuple[int, int, int, int]:
        pass

from src.core.dicts import VideoInfoDict
from src.utils import singleton


@singleton
class ProcessorGlobalVar:
    def __init__(self):
        self._data: VideoInfoDict = {}

    def get_data(self) -> VideoInfoDict:
        return self._data

    def get(self, key: str):
        if key not in VideoInfoDict.__annotations__:
            raise KeyError(f"{key} is not a valid key.")
        return self._data.get(key)

    def update(self, key: str, value):
        if key not in VideoInfoDict.__annotations__:
            raise KeyError(f"{key} is not a valid key.")

        self._data[key] = value

    def clear(self):
        self._data.clear()

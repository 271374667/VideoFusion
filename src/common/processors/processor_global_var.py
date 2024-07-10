from src.utils import singleton


@singleton
class ProcessorGlobalVar:
    def __init__(self):
        self._data: dict = {}

    def get(self, key):
        return self._data.get(key)

    def update(self, key, value):
        self._data[key] = value

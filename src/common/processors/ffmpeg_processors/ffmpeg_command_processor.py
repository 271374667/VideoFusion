from pathlib import Path

from src.common.processors.base_processor import FFmpegProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.core.datacls import VideoInfo


class FFmpegCommandProcessor(FFmpegProcessor):
    def __init__(self):
        super().__init__()
        self._processor_global_var: ProcessorGlobalVar = ProcessorGlobalVar()

    def process(self, data: VideoInfo) -> Path:
        return data

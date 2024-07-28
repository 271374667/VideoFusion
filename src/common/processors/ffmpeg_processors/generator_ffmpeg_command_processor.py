from src.common.processors.base_processor import FFmpegProcessor
from src.core.datacls import VideoInfo
from pathlib import Path


class GeneratorFFmpegCommandProcessor(FFmpegProcessor):
    def process(self, data: VideoInfo) -> Path:


        return data

from pathlib import Path

from src.common.ffmpeg_handler import FFmpegHandler
from src.common.processors.audio_processors.audio_ffmpeg_processor import AudioFFmpegProcessor
from src.common.processors.base_processor import AudioProcessor, AudioProcessorManager as APM


class AudioProcessorManager(APM):
    def __init__(self):
        super().__init__()
        self._ffmpeg_handler = FFmpegHandler()
        self._audio_ffmpeg_processor = AudioFFmpegProcessor()

        self._processors: list[AudioProcessor] = [
                self._audio_ffmpeg_processor
                ]

    def get_processors(self) -> list[AudioProcessor]:
        return self._processors

    def add_processor(self, processor: AudioProcessor):
        self._processors.append(processor)

    def process(self, x: Path) -> Path:
        for processor in self._processors:
            x = processor.process(x)
        return x

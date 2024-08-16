from pathlib import Path

from src.common.processors.base_processor import BaseProcessorManager, EXEProcessor
from src.common.processors.exe_processors.auto_editor_processor import AutoEditProcessor
from src.common.processors.exe_processors.audio_separator_processor import AudioSeparatorProcessor
from src.config import cfg, AudioSeparationAlgorithm


class EXEProcessorManager(BaseProcessorManager[Path]):
    def __init__(self):
        super().__init__()
        self._audio_separator_processor = AudioSeparatorProcessor()
        self._auto_edit_processor = AutoEditProcessor()

        self._processors: list[EXEProcessor] = [
            self._audio_separator_processor,
            self._auto_edit_processor
        ]

    def get_processors(self) -> list[EXEProcessor]:
        return self._processors

    def add_processor(self, processor: EXEProcessor):
        self._processors.append(processor)

    def process(self, x: Path) -> Path:
        self._check_enabled_processors()

        for processor in self._processors:
            if not processor.is_enable:
                continue
            x = processor.process(x)
        return x

    def _check_enabled_processors(self):
        """读取配置文件，判断哪些处理器是启用的
        """
        video_auto_cut_enabled: bool = cfg.get(cfg.video_auto_cut)
        self._auto_edit_processor.is_enable = video_auto_cut_enabled

        audio_separation_algorithm: AudioSeparationAlgorithm = cfg.get(cfg.audio_separation_algorithm)
        if audio_separation_algorithm == AudioSeparationAlgorithm.Disable:
            self._audio_separator_processor.is_enable = False

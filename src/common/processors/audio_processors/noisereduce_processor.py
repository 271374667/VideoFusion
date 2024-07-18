from pathlib import Path

from src.common.ffmpeg_handler import FFmpegHandler
from src.common.processors.base_processor import AudioProcessor
from src.config import AudioNoiseReduction, cfg


class NoisereduceProcessor(AudioProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ffmpeg_handler = FFmpegHandler()

    def process(self, input_wav_path: Path) -> Path:
        audio_noise_reduction: AudioNoiseReduction = cfg.get(cfg.audio_noise_reduction)
        if audio_noise_reduction == AudioNoiseReduction.DISABLE:
            return input_wav_path

        return self._ffmpeg_handler.noisereduce(input_wav_path, audio_noise_reduction)


if __name__ == '__main__':
    processor = NoisereduceProcessor()
    processor.process(Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\752d3c14f5a348f680a50ae66ffec66f.wav"))
    print("降噪完成")

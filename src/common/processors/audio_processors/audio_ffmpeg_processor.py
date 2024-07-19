from pathlib import Path

from src.common.ffmpeg_handler import FFmpegHandler
from src.common.processors.base_processor import AudioProcessor
from src.config import AudioNoiseReduction, AudioNormalization, AudioSampleRate, cfg


class AudioFFmpegProcessor(AudioProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ffmpeg_handler = FFmpegHandler()

    def process(self, input_wav_path: Path) -> Path:
        audio_filters: list[str] = []

        # 音频降噪
        audio_noise_reduction_mode: AudioNoiseReduction = cfg.get(cfg.audio_noise_reduction)
        if audio_noise_reduction_mode == AudioNoiseReduction.AI:
            audio_filters.append(f"{audio_noise_reduction_mode.value}".replace('\\', '/'))
        elif audio_noise_reduction_mode == AudioNoiseReduction.STATIC:
            audio_filters.append(audio_noise_reduction_mode.value)

        # 音频标准化
        audio_normalization: AudioNormalization = cfg.get(cfg.audio_normalization)
        if audio_normalization != AudioNormalization.DISABLE:
            audio_filters.append(audio_normalization.value)

        # 音频重新采样
        audio_sample_rate: AudioSampleRate = cfg.get(cfg.audio_sample_rate)
        audio_filters.append(
            f"aresample={audio_sample_rate.value}:resampler=soxr:precision=28:osf=s16:dither_method=triangular")

        return self._ffmpeg_handler.audio_process(input_wav_path, audio_filter=audio_filters)


if __name__ == '__main__':
    processor = AudioFFmpegProcessor()
    print(processor.process(Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\1\视频(1)_out.wav")))
    print("降噪完成")

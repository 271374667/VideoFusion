import re
from pathlib import Path

import loguru
from PySide6.QtCore import QObject, Signal

from src.common.processors.base_processor import EXEProcessor
from src.signal_bus import SignalBus
from src.config import cfg, AudioSeparationAlgorithm

from audio_separator.separator import Separator

from src.core.paths import MODELS_DIR, OUTPUT_DIR
from src.common.ffmpeg_handler import FFmpegHandler
from src.utils import TempDir
from enum import Enum


class AudioSeparationType(Enum):
    Instructment = 0
    Vocal = 1


class AudioSeparator:
    def __init__(self, model_name: str, model_file_dir: Path = MODELS_DIR, output_dir: Path = OUTPUT_DIR):
        self._output_dir: Path = output_dir
        self._model_name: str = model_name
        self.separator = Separator(
            model_file_dir=model_file_dir,
            output_dir=output_dir
        )
        self.separator.load_model(model_name)

    @property
    def model_name(self) -> str:
        return self._model_name

    def separate_audio(self, input_file: str) -> tuple[Path, Path]:
        """分离音频
        Args:
            input_file: 输入音频文件路径(wav格式)

        Returns:
            tuple[Path, Path]: 分离后的音频文件路径,同样为wav格式(乐器,人声)
        """
        output_files = self.separator.separate(input_file)
        instrument_file_path: Path = self._output_dir / output_files[0]
        vocal_file_path: Path = self._output_dir / output_files[1]
        loguru.logger.debug(f"音频分离完成,分离路径如下: {instrument_file_path} {vocal_file_path}")
        return instrument_file_path, vocal_file_path


class AudioSeparatorRedirect(QObject):
    progress_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self._pre_progress: int = 0
        self._process_pattern = re.compile(r"^\s*(\d+)%\|.*?")

        self._signal_bus = SignalBus()

    def write(self, message):
        if match := self._process_pattern.match(message):
            progress = float(match[1])
        else:
            progress = 0.0

        progress = int(progress)

        if progress != self._pre_progress:
            self._pre_progress = min(progress, 100)
            self._signal_bus.set_detail_progress_current.emit(int(self._pre_progress))


def flush(self):
    pass


class AudioSeparatorProcessor(EXEProcessor):
    def __init__(self):
        super().__init__()

        self._signal_bus: SignalBus = SignalBus()
        self._temp_dir: TempDir = TempDir()
        self._audio_separator_redirect: AudioSeparatorRedirect = AudioSeparatorRedirect()
        self._ffmpeg_handler: FFmpegHandler = FFmpegHandler()

        self._signal_bus.system_message.connect(self._audio_separator_redirect.write)

    def process(self, input_file_path: Path) -> Path:
        audio_separator_algorithm: AudioSeparationAlgorithm = cfg.get(cfg.audio_separation_algorithm)
        match audio_separator_algorithm:
            case AudioSeparationAlgorithm.UVRMDXNETVocFTVocal:
                model_name = "UVR-MDX-NET-Voc_FT.onnx"
                audio_separator_type = AudioSeparationType.Vocal
            case AudioSeparationAlgorithm.UVRMDXNETVocFTInstructment:
                model_name = "UVR-MDX-NET-Voc_FT.onnx"
                audio_separator_type = AudioSeparationType.Instructment
            case AudioSeparationAlgorithm.MDX23CVocal:
                model_name = "MDX23C_D1581.ckpt"
                audio_separator_type = AudioSeparationType.Vocal
            case AudioSeparationAlgorithm.MDX23CInstructment:
                model_name = "MDX23C_D1581.ckpt"
                audio_separator_type = AudioSeparationType.Instructment
            case AudioSeparationAlgorithm.BsRoformerVocal:
                model_name = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"
                audio_separator_type = AudioSeparationType.Vocal
            case AudioSeparationAlgorithm.BsRoformerInstructment:
                model_name = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"
                audio_separator_type = AudioSeparationType.Instructment
            case _:
                loguru.logger.error(f"未知的音频分离算法: {audio_separator_algorithm}")
                raise ValueError(f"未知的音频分离算法: {audio_separator_algorithm}")

        input_audio_path: Path = self._ffmpeg_handler.extract_audio_from_video(input_file_path)

        self._signal_bus.set_detail_progress_max.emit(100)
        audio_separator = AudioSeparator(model_name, output_dir=self._temp_dir.get_temp_dir())
        instrument_file_path, vocal_file_path = audio_separator.separate_audio(str(input_audio_path))

        result_audio_path: Path = instrument_file_path if audio_separator_type == AudioSeparationType.Instructment else vocal_file_path
        final_file_path: Path = self._ffmpeg_handler.replace_video_audio(input_file_path, result_audio_path)
        self._signal_bus.set_detail_progress_finish.emit()
        return final_file_path


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from src.components.cmd_text_edit import CMDTextEdit
    from src.signal_bus import SignalBus
    import threading


    def main():
        audio_separator_processor = AudioSeparatorProcessor()
        print(audio_separator_processor.process(
            Path(
                r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\测试\去黑边\d41a71f1c171b148cb41006193d3bc70.mp4")))


    app = QApplication([])
    cmd_text_edit = CMDTextEdit()
    cmd_text_edit.show()
    threading.Thread(target=main).start()
    app.exec()

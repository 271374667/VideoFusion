import re
import subprocess
from pathlib import Path

import cv2
import loguru

from src.config import VideoCodec, cfg
from src.core.paths import FFMPEG_FILE
from src.signal_bus import SignalBus


class FFmpegHandler:
    def __init__(self):
        self._signal_bus = SignalBus()
        self._ffmpeg_path: Path = FFMPEG_FILE

        if not self._ffmpeg_path.exists():
            self._signal_bus.failed.emit()
            loguru.logger.error(f"FFmpeg文件不存在: {self._ffmpeg_path}")
            raise FileNotFoundError(f"FFmpeg文件不存在: {self._ffmpeg_path}")

    def compress_video(self, input_file: Path, output_file: Path):
        # 生成压缩命令
        codec: VideoCodec = cfg.get(cfg.output_codec)
        command = self._get_ffmpeg_command(input_file, output_file, video_codec=codec.value)
        # 获取视频总帧数
        total_frame = self._get_video_total_frame(input_file)

        loguru.logger.debug(f"FFmpeg命令: {command}")
        self._run_command(command, total_frame)

    def _get_video_total_frame(self, video_path: Path) -> int:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError("无法打开视频")

        total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return total_frame

    def _get_ffmpeg_command(self,
                            input_video_path: Path,
                            output_video_path: Path,
                            video_filter: list[str] | None = None,
                            audio_filter: list[str] | None = None,
                            video_codec: str | None = None,
                            audio_codec: str | None = None
                            ) -> str:
        command: str = f'"{self._ffmpeg_path}" -i "{input_video_path}" '
        if video_filter:
            command += '-filter_complex '
            command += ' '.join(video_filter)

        if audio_filter:
            command += '-af '
            command += ' '.join(audio_filter)

        if audio_codec:
            command += f'{audio_codec}'

        if video_codec:
            command += f'{video_codec}'

        command += f' "{output_video_path}"'
        return command

    def _run_command(self, command: str, progress_total: int = 0):
        if not command:
            raise ValueError("命令不能为空")

        if ' -y' not in command:
            # -y参数表示覆盖输出文件,没有这个参数会提示是否覆盖导致程序卡住
            command += ' -y'

        self._signal_bus.set_detail_progress_reset.emit()
        if progress_total > 0:
            self._signal_bus.set_detail_progress_max.emit(progress_total)

        # Use a context manager to ensure the subprocess is properly cleaned up
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, encoding='utf-8', shell=True) as process:
            # 更新进度条
            for line in iter(process.stdout.readline, ''):
                loguru.logger.debug(line.strip())
                if progress_total > 0:
                    if match := re.search(r'frame=\s*(\d+)', line):
                        current_frame = int(match[1])
                        self._signal_bus.set_detail_progress_current.emit(current_frame)
                        if current_frame >= progress_total:
                            break
                elif line == '':
                    break

            # 等待子进程完成并读取所有剩余的输出
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                loguru.logger.critical(f"FFmpeg命令运行失败: {command}, 错误信息: {stderr}")
                self._signal_bus.failed.emit()
                raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

        self._signal_bus.set_detail_progress_finish.emit()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    # 绑定信号
    signal_bus = SignalBus()
    signal_bus.set_detail_progress_max.connect(lambda x: print(f"set_detail_progress_max: {x}"))
    signal_bus.set_detail_progress_current.connect(lambda x: print(f"set_detail_progress_current: {x}"))
    signal_bus.set_detail_progress_finish.connect(lambda: print("set_detail_progress_finish"))
    signal_bus.failed.connect(lambda: print("failed"))
    signal_bus.set_detail_progress_reset.connect(lambda: print("set_detail_progress_reset"))

    video_input_path: Path = Path(
            r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\752d3c14f5a348f680a50ae66ffec66f.mp4")
    video_output_path: Path = video_input_path.with_stem(f"{video_input_path.stem}_out")
    f = FFmpegHandler()
    f.compress_video(video_input_path, video_output_path)

    app.exec()

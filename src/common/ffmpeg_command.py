import re
import subprocess
from pathlib import Path

import cv2

from src.core.paths import FFMPEG_FILE
from src.signal_bus import SignalBus


class FFmpegCommand:
    def __init__(self, input_file_path: Path | str, input_output_file: Path | str):
        self._signal_bus: SignalBus = SignalBus()
        self.ffmpeg_bin: Path = FFMPEG_FILE
        self.input_file_path = Path(input_file_path)
        self.output_file_path = Path(input_output_file)

    def compact_video(self):
        cmd = f'ffmpeg -y -hide_banner -i "{self.input_file_path}" -vf "scale=160:100" -c:v libx264 -crf 23 -preset slow -qcomp 0.5 -psy-rd 0.3:0 -aq-mode 2 -aq-strength 0.8 -b:a 256k "{self.output_file_path}"'
        self._run_command(cmd)

    def _run_command(self, command: str):
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_description.emit("压缩视频")
        self._signal_bus.set_total_progress_max.emit(1)

        # 获取视频的总帧数
        cap = cv2.VideoCapture(str(self.input_file_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._signal_bus.set_detail_progress_max.emit(total_frames)
        cap.release()

        # 运行ffmpeg命令
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   universal_newlines=True, encoding='gbk')

        # 更新进度条
        for line in iter(process.stdout.readline, ''):
            if match := re.search(r'frame=\s*(\d+)', line):
                current_frame = int(match[1])
                self._signal_bus.set_detail_progress_current.emit(current_frame)
                if current_frame >= total_frames:
                    break

        # 等待子进程完成并读取所有剩余的输出
        process.communicate()

        # 终止子进程
        process.kill()
        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()


def test_ffmpeg_command():
    # 创建一个 FFmpegCommand 实例
    ffmpeg_command = FFmpegCommand(r"E:\load\python\Project\VideoMosaic\测试\video\001.mp4",
                                   r"E:\load\python\Project\VideoMosaic\测试\video\001_out.mp4")

    # 连接信号
    ffmpeg_command._signal_bus.set_total_progress_reset.connect(lambda: print("Total progress reset"))
    ffmpeg_command._signal_bus.set_detail_progress_reset.connect(lambda: print("Detail progress reset"))
    ffmpeg_command._signal_bus.set_total_progress_description.connect(
            lambda desc: print(f"Total progress description: {desc}"))
    ffmpeg_command._signal_bus.set_total_progress_max.connect(lambda x: print(f"Total progress max: {x}"))
    ffmpeg_command._signal_bus.set_detail_progress_max.connect(lambda x: print(f"Detail progress max: {x}"))
    ffmpeg_command._signal_bus.set_detail_progress_current.connect(
            lambda current: print(f"Detail progress current: {current}"))

    # 调用方法
    ffmpeg_command.compact_video()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    test_ffmpeg_command()
    print('finished')
    app.exec()

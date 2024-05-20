import re
import subprocess
from pathlib import Path

import cv2

from src.core.paths import FFMPEG_FILE
from src.signal_bus import SignalBus


class FFmpegCommand:
    def __init__(self):
        self._signal_bus: SignalBus = SignalBus()
        self.ffmpeg_bin: Path = FFMPEG_FILE

    def compress_video(self, input_file_path: Path | str, output_file_path: Path | str):
        input_file_path = Path(input_file_path)
        output_file_path = Path(output_file_path)
        cmd = f'ffmpeg -y -hide_banner -i "{input_file_path}" -vf "scale=160:100" -c:v libx264 -crf 23 -preset slow -qcomp 0.5 -psy-rd 0.3:0 -aq-mode 2 -aq-strength 0.8 -b:a 256k "{output_file_path}"'
        self._reset_progress("压缩视频")
        self._signal_bus.set_total_progress_max.emit(1)
        self._run_command(input_file_path, cmd)
        self._signal_bus.set_total_progress_finish.emit()

    def audio_extract(self, input_video_path_list: list[str | Path], output_file_path: str | Path) -> Path:
        """
        通过ffmpeg提取视频文件中的音频，并将它们按照传入的顺序合并为单个音频文件。

        参数:
        input_video_path_list: 包含视频文件路径的列表。
        output_file_path: 合并后的音频输出路径。

        Returns:
        合并后的音频文件的路径
        """
        self._reset_progress("合并音频")
        # 确保输出文件路径是Path对象，以便进行操作
        output_file_path = Path(output_file_path)

        # 生成临时文件路径列表，用于存储每个视频提取出的音频
        extracted_audios: list[Path] = [output_file_path.parent / f"temp_audio_{i}.mp3" for i, _ in
                enumerate(input_video_path_list)]
        self._signal_bus.set_total_progress_max.emit(len(extracted_audios))

        # 提取每个视频文件中的音频
        for video_path, temp_audio in zip(input_video_path_list, extracted_audios):
            cmd_extract = f"ffmpeg -i {video_path} -q:a 0 -map a {temp_audio}"
            self._run_command(video_path, cmd_extract)
            self._signal_bus.advance_total_progress.emit(1)

        # 生成ffmpeg合并命令中的输入文件列表部分
        inputs_concat = ' '.join([f"-i {audio_path}" for audio_path in extracted_audios])

        # ffmpeg的filter_complex选项用于合并音频
        filter_complex = f"concat=n={len(extracted_audios)}:v=0:a=1"

        # ffmpeg命令合并音频并输出到指定路径
        cmd_merge = f"ffmpeg {inputs_concat} -filter_complex {filter_complex} -y {output_file_path}"
        if output_file_path.exists():
            output_file_path.unlink()
        subprocess.run(cmd_merge, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, )

        # 完成合并后，删除临时音频文件
        for temp_audio in extracted_audios:
            temp_audio.unlink()

        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        return output_file_path

    def merge_video_with_audio(self, input_video_path: str | Path, input_audio_path: str | Path):
        input_video_path = Path(input_video_path)
        input_audio_path = Path(input_audio_path)
        output_file_path = input_video_path.parent / f"{input_video_path.stem}_merged.mp4"
        if output_file_path.exists():
            output_file_path.unlink()
        cmd = f'ffmpeg -y -hide_banner -i "{input_video_path}" -i "{input_audio_path}" -c:v copy -c:a aac -strict experimental "{output_file_path}"'
        self._reset_progress("合并音频")
        self._signal_bus.set_total_progress_max.emit(1)
        self._run_command(input_video_path, cmd)
        self._signal_bus.set_total_progress_finish.emit()

    def _reset_progress(self, total_progress_desc: str):
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_description.emit(total_progress_desc)

    def _run_command(self, input_file_path: str | Path, command: str):
        # 获取视频的总帧数
        cap = cv2.VideoCapture(str(input_file_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._signal_bus.set_detail_progress_max.emit(total_frames)
        cap.release()

        # 运行ffmpeg命令
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   universal_newlines=True, encoding='utf-8')

        # # 更新进度条
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
        self._signal_bus.set_detail_progress_finish.emit()


def test_ffmpeg_command():
    # 创建一个 FFmpegCommand 实例
    ffmpeg_command = FFmpegCommand()

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


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    test_ffmpeg_command()
    print('finished')
    app.exec()

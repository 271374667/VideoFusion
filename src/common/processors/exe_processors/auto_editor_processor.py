import re
import sys
from os import environ
from pathlib import Path

import loguru
from PySide6.QtCore import QObject, Signal
from auto_editor.edit import edit_media
from auto_editor.ffwrapper import FFmpeg
from auto_editor.utils.log import Log
from auto_editor.utils.types import Args

from src.components.cmd_text_edit import CMDTextEdit
from src.core.paths import FFMPEG_FILE
from src.signal_bus import SignalBus
from src.utils import TempDir, get_output_file_path
from src.common.processors.base_processor import EXEProcessor


class AutoEditRedirect(QObject):
    title_signal = Signal(str)
    progress_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self._signal_bus = SignalBus()
        self._pre_title: str = ''
        self._pre_progress: int = 0
        self._process_pattern = re.compile(r".*?&\s*(?P<title>[\w\s]+)\s*\[.*]\s*(?P<progress>\d+\.\d+)%")

    def write(self, message):
        if match := re.search(self._process_pattern, message):
            title = match["title"].strip()
            progress = float(match["progress"]) if (match := re.search(self._process_pattern, message)) else 0.0
            progress = int(progress)

            if title != self._pre_title:
                self._pre_title = title
                self.title_signal.emit(title)
                loguru.logger.debug(f'自动剪辑进度: {title}')

            if progress != self._pre_progress:
                self._pre_progress = min(progress, 100)
                self._signal_bus.set_detail_progress_current.emit(int(self._pre_progress))
        sys.__stdout__.write(message)
        sys.__stdout__.flush()

    def flush(self):
        pass


class AutoEditProcessor(EXEProcessor):
    def __init__(self):
        self._signal_bus = SignalBus()
        self._auto_edit_redirect = AutoEditRedirect()
        self._signal_bus.system_message.connect(self._auto_edit_redirect.write)

    def process(self, input_file: Path) -> Path:
        output_file = get_output_file_path(Path(input_file), process_info="_auto_edit")
        ffmpeg = FFmpeg(ff_location=str(FFMPEG_FILE), my_ffmpeg=True)  # 初始化FFmpeg
        temp = TempDir().get_temp_dir()  # 临时目录

        # 确保临时目录存在
        temp.mkdir(parents=True, exist_ok=True)

        # 创建 Args 对象并设置参数
        args = Args(str(input_file), str(output_file))
        args.silent_speed = 8
        args.video_speed = 1
        args.frame_margin = 3
        args.edit = '(audio > 0.025)'
        args.progress = 'ascii'
        args.output_file = output_file
        args.ffmpeg_location = str(FFMPEG_FILE)
        args.show_ffmpeg_output = True
        args.no_open = True

        ff_color = "AV_LOG_FORCE_NOCOLOR"
        no_color = bool(environ.get("NO_COLOR")) or bool(environ.get(ff_color))
        log = Log(no_color=no_color)  # 创建日志对象
        paths = [str(input_file)]  # 输入文件路径列表

        # 调用 edit_media 函数进行视频编辑
        self._signal_bus.set_detail_progress_max.emit(100)
        edit_media(paths, ffmpeg, args, str(temp), log)
        loguru.logger.success(f"视频剪辑完成，输出文件为: {output_file}")
        return output_file


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import threading

    app = QApplication([])
    cmd_text_edit = CMDTextEdit()
    cmd_text_edit.show()

    auto_edit_redirect = AutoEditRedirect()
    # sys.stdout = auto_edit_redirect
    auto_edit_redirect.title_signal.connect(lambda title: print(title))
    auto_edit_redirect.progress_signal.connect(lambda progress: print(progress))


    def run():
        input_video_path = r"D:\Games\OBS录像\mkdocs\002降噪\001 mkdocs 欢迎您.mp4"
        auto_edit_processor = AutoEditProcessor()
        print(auto_edit_processor.process(Path(input_video_path)))


    threading.Thread(target=run).start()

    app.exec()

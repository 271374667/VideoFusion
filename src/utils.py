import atexit
import contextlib
import ctypes
import json
import os
import shutil
import subprocess
import threading
import time
from functools import wraps
from pathlib import Path
from typing import Callable, Optional, Tuple
from urllib import error, request

import loguru
from PySide6.QtCore import QObject, QThread, Signal

from src.config import cfg
from src.core.paths import FFPROBE_FILE


def singleton(cls):
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


def timit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        loguru.logger.debug(f"\n{func.__name__}执行时间:{end_time - start_time}\n")
        return result

    return wrapper


def thread_with_timeout(timeout: int):
    """线程超时自动杀死

    通过调用底层CPython的代码将线程超时自动杀死

    Example:
        @thread_with_timeout(5)
            def target_function():
                for i in range(10):
                    print(f"Doing task {i}")
                    time.sleep(1)  # Simulate time-consuming task
        target_function()

    Args:
        timeout: 超时时间，单位秒
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            def run_func():
                with contextlib.suppress(SystemExit):
                    func(*args, **kwargs)

            def timer():
                time.sleep(timeout)
                if thread.is_alive():
                    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident),
                                                                     ctypes.py_object(SystemExit))
                    if res > 1:
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, 0)
                        loguru.logger.error('Error: could not terminate thread')
                    else:
                        loguru.logger.debug(f'Thread {thread.ident} forcefully terminated')

            thread = threading.Thread(target=run_func)
            thread.start()

            timer_thread = threading.Thread(target=timer)
            timer_thread.start()

        return wrapper

    return decorator


class ForceStopThread:
    def __init__(self):
        self.thread = None
        self.thread_id = None

    def start_task(self, func, *args, **kwargs):
        if self.thread:
            self.stop_task()

        def run():
            self.thread_id = threading.get_ident()
            with contextlib.suppress(SystemExit):
                func(*args, **kwargs)

        self.thread = threading.Thread(target=run)
        self.thread.start()

    def stop_task(self):
        if self.thread is not None and self.thread.is_alive():
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.thread_id),
                                                             ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(self.thread_id, 0)
                loguru.logger.error('Error: could not terminate thread')
            else:
                loguru.logger.debug(f'Thread {self.thread_id} forcefully terminated')


def calculate_dimensions(width: int, height: int, target_width: int, target_height: int):
    if width == 0 or height == 0:
        loguru.logger.critical("视频的宽度或高度为0, 请检查视频")
        raise ValueError("Width or height is 0")
    scale = min(target_width / width, target_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    pad_top = (target_height - new_height) // 2
    pad_bottom = target_height - new_height - pad_top
    pad_left = (target_width - new_width) // 2
    pad_right = target_width - new_width - pad_left
    return new_width, new_height, pad_top, pad_bottom, pad_left, pad_right


def evenly_distribute_numbers(current_num: int, target_num: int) -> list[int]:
    """平滑抽帧"""
    if current_num <= target_num:
        raise ValueError("current_num must be greater than target_num")

    diff = current_num - target_num  # 需要移除的数字个数
    interval = current_num / diff  # 平均间隔

    # 生成初始列表
    numbers = list(range(current_num))

    # 移除均匀间隔位置的数字
    for i in range(diff):
        remove_index = int(round(i * interval))
        if remove_index < len(numbers):
            numbers.pop(remove_index)

    return numbers


def evenly_interpolate_numbers(current_num: int, target_num: int) -> list[int]:
    """平滑插值"""
    if current_num >= target_num:
        raise ValueError("current_num must be less than target_num")

    diff = target_num - current_num  # 需要增加的数字个数
    interval = (current_num - 1) / (diff + 1)  # 插入位置的平均间隔

    # 生成初始列表
    numbers = list(range(current_num))
    new_numbers = []

    # 计算所有插入点
    insert_positions = [round((i + 1) * interval) for i in range(diff)]

    # 均匀插入数字
    insert_index = 0
    for i in range(current_num):
        new_numbers.append(numbers[i])
        # 在插入点插入数字
        if insert_index < diff and i + 1 >= insert_positions[insert_index]:
            new_numbers.append(numbers[i])
            insert_index += 1

    return new_numbers


def trans_second_to_human_time(second: int) -> str:
    """
    感谢'0<0'童鞋写本开源项目做出的共享
    """
    if second // 60 == 0:
        return f"{second}秒"
    elif second // 60 < 60:
        minute = second // 60
        second %= 60
        return f"{str(minute)}分{second}秒"
    else:
        hour = second // 3600
        minute = (second - hour * 60 * 60) // 60
        second = second - hour * 3600 - minute * 60
        return f"{str(hour)}小时{str(minute)}分{second}秒"


def check_file_readability(file_path: Path) -> bool:
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'r'):
            return True
    except IOError as e:
        loguru.logger.error(f'文件{file_path}不可读: {e}')
        return False


def get_audio_sample_rate(file_path: Path) -> int:
    # 使用FFmpeg命令获取媒体文件的信息，并输出为json格式
    cmd = [
        FFPROBE_FILE,
        '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'stream=sample_rate',
        '-of', 'json',
        file_path
    ]

    # 运行FFmpeg命令并获取输出
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
                            creationflags=subprocess.CREATE_NO_WINDOW)

    # 解析输出的json数据
    output = json.loads(result.stdout)
    loguru.logger.debug(f'视频信息:{output}')

    return int(output['streams'][0]['sample_rate'])


def get_output_file_path(input_file_path: Path, process_info: str = "out") -> Path:
    return TempDir().get_temp_dir() / f"{input_file_path.stem}_{process_info}{input_file_path.suffix}"


def move_file_to_output_dir(video_list: list[Path]) -> Path:
    output_dir: Path = Path(cfg.get(cfg.output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)

    # 将视频移动到输出目录
    for video in video_list:
        output_video = output_dir / video.name
        video.replace(output_video)
        loguru.logger.debug(f"移动文件:{video} -> {output_video}")
    return output_dir


def is_available_video_file(video_path: str | Path) -> bool:
    video_path = Path(video_path)
    if not video_path.exists():
        return False
    if not video_path.is_file():
        return False
    if video_path.suffix.lower() not in ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.ts']:
        return False
    return True


@singleton
class TempDir:
    def __init__(self, temp_dir: Path | None = None):
        self.path = temp_dir or Path(cfg.get(cfg.temp_dir))
        self._is_exists: bool = False

        delete_temp_dir: bool = cfg.get(cfg.delete_temp_dir)

        if delete_temp_dir:
            @atexit.register
            def delete_temp_dir():
                self.delete_dir()

    @property
    def temp_dir(self) -> Path:
        return self.get_temp_dir()

    def get_temp_dir(self) -> Path:
        if self.path.exists():
            return self.path

        self.path.mkdir(parents=True, exist_ok=True)
        loguru.logger.debug(f"创建临时文件夹:{self.path}")
        return self.path

    def delete_dir(self) -> None:
        if not self.path.exists():
            loguru.logger.debug(f'文件夹不存在:{self.path},无法删除')
            return

        shutil.rmtree(self.path, ignore_errors=True)
        loguru.logger.debug(f"删除临时文件夹:{self.path}")


class WorkThread(QObject):
    finished_signal = Signal()
    result = Signal(object)

    def __init__(self):
        super().__init__()
        self.kwargs = None
        self.args = None
        self.func: Callable

    def set_start_func(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def start(self):
        if self.args or self.kwargs:
            func_return = self.func(*self.args, **self.kwargs)
        else:
            func_return = self.func()
        self.result.emit(func_return)
        self.finished_signal.emit()


class RunInThread(QObject):
    def __init__(self):
        super().__init__()
        self.finished_func: Optional[Callable] = None
        self.worker = WorkThread()
        self.mythread = QThread()
        self.worker.moveToThread(self.mythread)

        self.mythread.started.connect(self.worker.start)
        self.worker.finished_signal.connect(self.worker.deleteLater)
        self.worker.destroyed.connect(self.mythread.quit)
        self.mythread.finished.connect(self.mythread.deleteLater)
        self.mythread.destroyed.connect(self.deleteLater)

    def start(self):
        """当函数设置完毕之后调用start即可"""
        self.mythread.start()

    def set_start_func(self, func, *args, **kwargs):
        """设置一个开始函数

        这部分就是多线程运行的地方，里面可以是爬虫，可以是其他IO或者阻塞主线程的函数

        """
        self.worker.set_start_func(func, *args, **kwargs)

    def set_finished_func(self, func):
        """设置线程结束后的回调函数"""
        self.finished_func = func
        self.worker.result.connect(self._done_callback)

    def _done_callback(self, *args, **kwargs):
        if len(args) == 2 or kwargs:
            self.finished_func(*args, **kwargs)
        elif len(args) == 1:
            self.finished_func(args[0])
        else:
            self.finished_func()


class VersionRequest:
    # 定义线程超时异常
    class TimeoutException(Exception):
        pass

    # 定义用于超时控制的函数
    def _raise_timeout(self, signum, frame):
        raise self.TimeoutException

    # 定义重试装饰器
    @staticmethod
    def retry(retries: int):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for _ in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        time.sleep(1)  # 重试间隔时间
                loguru.logger.debug(f"正在进行第{retries}次重试获取最新版本, 上一次的报错信息为: {last_exception}")
                return None, None

            return wrapper

        return decorator

    # 定义多线程装饰器
    @staticmethod
    def timeout(seconds: int):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = [None]

                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except VersionRequest.TimeoutException:
                        result[0] = (None, None)

                thread = threading.Thread(target=target)
                thread.start()
                thread.join(seconds)
                if thread.is_alive():
                    loguru.logger.debug(f"正在进行第{seconds}秒超时处理, 请稍后重试")
                    result[0] = (None, None)
                return result[0]

            return wrapper

        return decorator

    @retry(retries=3)
    @timeout(seconds=20)
    def get_latest_version(self) -> Tuple[Optional[str], Optional[str]]:
        url = "https://api.github.com/repos/271374667/VideoFusion/releases/latest"
        try:
            with request.urlopen(url) as response:
                if response.status != 200:
                    return None, None
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get("tag_name")
                release_notes = data.get("body")
                return latest_version, release_notes
        except error.URLError as e:
            loguru.logger.error(f'获取最新版本失败: {e}')
            return None, None


if __name__ == '__main__':
    # 抽帧示例用法
    # current_num = 180000
    # target_num = 150000
    # result = evenly_distribute_numbers(current_num, target_num)
    # print(f"抽帧:{result}")
    # print(len(result)) [0, 0, 1, 2, 2, 3]

    # # 插帧示例用法
    # current_num = 1148
    # target_num = 1500
    # start = time.time()
    # result = evenly_interpolate_numbers(current_num, target_num)
    # print(time.time() - start)
    # print(f"插帧:{result}")

    # v = VersionRequest()
    # version, notes = v.get_latest_version()
    # print(f"Latest Version: {version}, Release Notes: {notes}")
    ...

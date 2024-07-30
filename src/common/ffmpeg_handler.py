import os
import re
import subprocess
from pathlib import Path

import cv2
import loguru

from src.config import AudioNoiseReduction, AudioSampleRate, FrameRateAdjustment, VideoCodec, cfg
from src.core import FFMPEG_ERROR_WORDS
from src.core.paths import FFMPEG_FILE, ROOT
from src.signal_bus import SignalBus
from src.utils import TempDir, get_output_file_path

# ffmpeg的AI降噪模型需要在项目目录下运行
os.chdir(ROOT)


class FFmpegHandler:
    def __init__(self):
        # ffmpeg错误关键字,这些字会在终端中被标红,全部小写
        self.FFMPEG_ERROR_WORD: list[str] = FFMPEG_ERROR_WORDS

        self._temp_dir = TempDir()
        self._signal_bus = SignalBus()
        self._ffmpeg_path: Path = FFMPEG_FILE

        if not self._ffmpeg_path.exists():
            self._signal_bus.failed.emit()
            loguru.logger.error(f"FFmpeg文件不存在: {self._ffmpeg_path}")
            raise FileNotFoundError(f"FFmpeg文件不存在: {self._ffmpeg_path}")

    def reencode_video(self, input_file_path: Path) -> Path:
        """
        重新编译指定的视频文件。

        此方法接收一个视频文件路径作为输入，根据配置中指定的视频编解码器和音频采样率对视频进行压缩处理，
        并将压缩后的视频保存在临时目录下，文件名为原视频文件名加上 "_reencode" 后缀。

        Args:
            input_file_path (Path): 输入视频文件的路径。该视频文件将被压缩。

        Returns:
            Path: 重新编译后的视频文件的路径。

        Example:
            >>> ffmpeg_handler = FFmpegHandler()
            >>> input_video_path = Path("/path/to/video.mp4")
            >>> reencode_video_path = ffmpeg_handler.reencode_video(input_video_path)
            >>> print(reencode_video_path)
            Path("/path/to/temp_dir/video_compressed.mp4")

        注意:
            - 压缩过程中使用的视频编解码器和音频采样率由配置文件中的 `output_codec` 和 `audio_sample_rate` 决定。
            - 输出视频文件将保存在临时目录中。
        """
        output_file_path: Path = get_output_file_path(input_file_path, "reencode").with_suffix('.mp4')

        # 生成压缩命令
        video_codec: VideoCodec = cfg.get(cfg.output_codec)

        audio_sample_rate: AudioSampleRate = cfg.get(cfg.audio_sample_rate)
        audio_sample_rate = audio_sample_rate.value
        audio_filter = [f"aresample={audio_sample_rate}:resampler=soxr:precision=28:osf=s16:dither_method=triangular"]
        audio_codec = f' -c:a aac -b:a {audio_sample_rate} -strict experimental -vsync 1'

        video_filter = []
        frame_rate_adjustment_type: FrameRateAdjustment = cfg.get(cfg.rate_adjustment_type)
        framerate: int = cfg.get(cfg.video_fps)
        if frame_rate_adjustment_type == FrameRateAdjustment.NORMAL:
            video_filter.append(f"fps=fps={framerate}")
        elif frame_rate_adjustment_type == FrameRateAdjustment.MOTION_INTERPOLATION:
            video_filter.append(
                    f"minterpolate='mi_mode=mci:mc_mode=aobmc:me_mode=bidir:mb_size=16:vsbmc=1:fps={framerate}'")

        command = self._get_ffmpeg_command(input_file_path,
                                           output_file_path,
                                           audio_filter=audio_filter,
                                           video_codec=video_codec.value,
                                           video_filter=video_filter,
                                           audio_codec=audio_codec)
        # 获取视频总帧数
        total_frame = self.get_video_total_frame(input_file_path)

        self.run_command(command, total_frame)
        return output_file_path

    def compress_video(self, input_file_path: Path) -> Path:
        """
        压缩指定的视频文件。

        此方法接收一个视频文件路径作为输入，根据配置中指定的视频编解码器和音频采样率对视频进行压缩处理，
        并将压缩后的视频保存在临时目录下，文件名为原视频文件名加上 "_compressed" 后缀。

        Args:
            input_file_path (Path): 输入视频文件的路径。该视频文件将被压缩。

        Returns:
            压缩后的视频文件的路径。
        """
        output_file_path: Path = get_output_file_path(input_file_path, "compressed").with_suffix('.mp4')

        # 生成压缩命令
        video_codec: VideoCodec = cfg.get(cfg.output_codec)
        audio_codec = ' -c:a copy '

        command = self._get_ffmpeg_command(input_file_path,
                                           output_file_path,
                                           video_codec=video_codec.value,
                                           audio_codec=audio_codec)
        # 获取视频总帧数
        total_frame = self.get_video_total_frame(input_file_path)

        self.run_command(command, total_frame)
        return output_file_path

    def extract_audio_from_video(self, input_file_path: Path) -> Path:
        """从视频文件中提取音频轨道，并保存为WAV格式。

        此方法接收一个视频文件的路径作为输入，然后提取该视频文件中的音频轨道，保存为WAV格式的文件。
        提取的音频文件将保存在与输入视频相同的目录下，文件名为原视频文件名加上.wav后缀。

        Args:
            input_file_path (Path): 输入视频文件的路径。该视频文件中的音频轨道将被提取出来。

        Returns:
            Path: 提取出的音频文件的路径。该文件为WAV格式。

        Example:
            >>> ffmpeg_handler = FFmpegHandler()
            >>> input_video_path = Path("/path/to/video.mp4")
            >>> extracted_audio_path = ffmpeg_handler.extract_audio_from_video(input_video_path)
            >>> print(extracted_audio_path)
            Path("/path/to/video.wav")

        注意:
            - 该方法仅支持将音频保存为WAV格式。
            - 如果输入视频文件中不包含音频轨道，将不会生成音频文件，并可能抛出异常。
        """
        output_file_path = get_output_file_path(input_file_path).with_suffix('.wav')
        has_audio: bool = self._check_audio_stream_with_ffmpeg(input_file_path)
        if not has_audio:
            self.run_command(
                    f'"{self._ffmpeg_path}" -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 "{output_file_path}"')
            return output_file_path
        other_command = [' -vn -acodec pcm_s16le ']
        command = self._get_ffmpeg_command(input_file_path,
                                           output_file_path,
                                           other_command=other_command)
        total_frame = self.get_video_total_frame(input_file_path)
        self.run_command(command, total_frame)
        return output_file_path

    def replace_video_audio(self, input_video_path: Path, audio_wav_path: Path) -> Path:
        """替换视频文件中的音频轨道。

        该方法接受一个视频文件路径和一个音频文件路径作为输入，
        将视频文件中的原有音频替换为指定的音频文件，然后返回替换音频后的视频文件的路径。

        Args:
            input_video_path (Path): 输入视频文件的路径。这个视频文件的音频轨道将被替换。
            audio_wav_path (Path): 要替换成的音频文件的路径。这个音频文件将替换视频文件中原有的音频轨道。

        Returns:
            Path: 替换音频后的视频文件的路径。

        Example:
            >>> ffmpeg_handler = FFmpegHandler()
            >>> input_video_path = Path("/path/to/video.mp4")
            >>> audio_wav_path = Path("/path/to/audio.wav")
            >>> output_video_path = ffmpeg_handler.replace_video_audio(input_video_path, audio_wav_path)
            >>> print(output_video_path)
            Path("/path/to/temp_dir/video_replace_audio.mp4")

        注意:
            - 输入的音频文件应为WAV格式。
            - 输出视频文件将保存在临时目录中，文件名格式为“原视频文件名_replace_audio.原视频文件扩展名”。
        """
        output_video_path = get_output_file_path(input_video_path, "replace_audio")
        other_command = [f'-i "{audio_wav_path}" -c:v copy -map 0:v:0 -map 1:a:0 -shortest']
        command = self._get_ffmpeg_command(input_video_path,
                                           output_video_path,
                                           other_command=other_command)
        self.run_command(command)
        return output_video_path

    def noisereduce(self, input_audio_path: Path, mode: AudioNoiseReduction = AudioNoiseReduction.AI) -> Path:
        """去噪音频文件。

        该方法接受一个音频文件路径作为输入，然后对音频文件进行去噪处理，
        返回去噪后的音频文件的路径。

        Args:
            input_audio_path (Path): 输入音频文件的路径。这个音频文件将被去噪。
            mode (AudioNoiseReduction): 去噪模式。默认为AI。

        Returns:
            输出音频文件的路径。
        """
        output_audio_path = get_output_file_path(input_audio_path, "denoise")
        model_value = mode.value
        if mode == AudioNoiseReduction.AI:
            audio_filter = [f"{model_value}".replace('\\', '/')]
            command = self._get_ffmpeg_command(input_audio_path,
                                               output_audio_path,
                                               audio_filter=audio_filter)
            self.run_command(command)
        elif mode == AudioNoiseReduction.STATIC:
            audio_filter = [model_value]
            command = self._get_ffmpeg_command(input_audio_path,
                                               output_audio_path,
                                               audio_filter=audio_filter)
            self.run_command(command)
        return output_audio_path

    def audio_process(self, input_audio_path: Path, audio_filter: list[str]) -> Path:
        """对音频文件进行处理。

        该方法接受一个音频文件路径和一个音频滤镜列表作为输入，对音频文件进行处理，
        并返回处理后的音频文件的路径。

        Args:
            input_audio_path (Path): 输入音频文件的路径。
            audio_filter (list[str]): 音频滤镜列表。

        Returns:
            处理后的音频文件的路径。
        """
        output_audio_path = get_output_file_path(input_audio_path, "audio_processed")
        command = self._get_ffmpeg_command(input_audio_path,
                                           output_audio_path,
                                           audio_filter=audio_filter)
        self.run_command(command)
        return output_audio_path

    def merge_videos(self, video_list: list[Path]) -> Path:
        """合并视频文件。

        该方法接受一个视频文件路径列表作为输入，将这些视频文件合并为一个视频文件，
        并返回合并后的视频文件的路径。

        Args:
            video_list (list[Path]): 要合并的视频文件路径列表。

        Returns:
            合并后的视频文件的路径。
        """
        temp_output_video_txt_path: Path = self._temp_dir.get_temp_dir() / 'output_video.txt'
        output_file: Path = get_output_file_path(video_list[0], "merged")
        with open(temp_output_video_txt_path, 'w', encoding='utf-8') as f:
            txt_content = [f"file '{video}'\n" for video in video_list]
            f.writelines(txt_content)

        command = f'"{self._ffmpeg_path}" -fflags +genpts -f concat -safe 0 -i "{temp_output_video_txt_path}" -c copy -bsf:a aac_adtstoasc -vsync 2 "{output_file}" -y'
        self.run_command(command)
        return output_file

    def encode_video_to_ts(self, input_video_path: Path) -> Path:
        """将视频文件编码为TS格式。

        该方法接受一个视频文件路径作为输入，将该视频文件编码为TS格式，
        并返回编码后的TS格式视频文件的路径。

        Args:
            input_video_path (Path): 输入视频文件的路径。

        Returns:
            编码后的TS格式视频文件的路径。
        """
        output_file: Path = get_output_file_path(input_video_path, "encode2ts").with_suffix('.ts')
        command = f'"{self._ffmpeg_path}" -fflags +genpts -i "{input_video_path}" -c copy -bsf:v h264_mp4toannexb -vsync 2 -f mpegts "{output_file}" -y'
        total_frame = self.get_video_total_frame(input_video_path)
        self.run_command(command, total_frame)
        return output_file

    def get_support_video_format(self) -> list[str]:
        """获取FFmpeg支持的视频格式

        Returns:
            list[str]: 支持的视频格式列表
            Example:
                ['.mp4', '.avi', '.mov', '.flv', '.wmv']
        """
        # 调用ffmpeg -formats命令获取所有支持的格式
        result = subprocess.run([self._ffmpeg_path, '-formats'], capture_output=True, text=True)
        formats = re.findall(r'D\s+([a-zA-Z0-9]+)', result.stdout)
        return [f'.{fmt}' for fmt in formats]

    def get_video_total_frame(self, video_path: Path) -> int:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError("无法打开视频")

        total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return total_frame

    def run_command(self, command: str, progress_total: int = 0):
        if not command:
            raise ValueError("命令不能为空")

        if ' -y' not in command:
            # -y参数表示覆盖输出文件,没有这个参数会提示是否覆盖导致程序卡住
            command += ' -y'

        loguru.logger.debug(f"FFmpeg命令: {command}")

        self._signal_bus.set_detail_progress_reset.emit()
        if progress_total > 0:
            self._signal_bus.set_detail_progress_max.emit(progress_total)

        # Use a context manager to ensure the subprocess is properly cleaned up
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, encoding='utf-8', shell=True) as process:
            # 更新进度条
            for line in iter(process.stdout.readline, ''):
                each_line = line.strip()
                if any(x in each_line.lower() for x in self.FFMPEG_ERROR_WORD):
                    loguru.logger.error(each_line)
                else:
                    loguru.logger.debug(each_line)
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

    def _check_audio_stream_with_ffmpeg(self, video_path: Path) -> bool:
        """使用ffmpeg命令检查视频文件是否包含音频流。
        """
        temp_audio_file = self._temp_dir.get_temp_dir() / video_path.name
        command = f'{self._ffmpeg_path} -i "{video_path}" -vn -acodec copy "{temp_audio_file}" -y'
        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True,
                           encoding='utf-8',
                           universal_newlines=True)
        except subprocess.CalledProcessError as e:
            loguru.logger.error(f"检查音频流失败: {e}")
            return False
        has_audio = temp_audio_file.exists()

        if not has_audio:
            loguru.logger.debug(f"视频文件{video_path}不包含音频流")

        return has_audio

    def _get_ffmpeg_command(self,
                            input_video_path: Path,
                            output_video_path: Path,
                            video_filter: list[str] | None = None,
                            audio_filter: list[str] | None = None,
                            video_codec: str | None = None,
                            audio_codec: str | None = None,
                            other_command: list[str] | None = None
                            ) -> str:
        command: str = f'"{self._ffmpeg_path}" -i "{input_video_path}" '
        has_audio: bool = self._check_audio_stream_with_ffmpeg(input_video_path)
        # 如果没有音频流，添加静音音频流
        silence_audio_command = ' -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -c:a aac -t 10 '
        if video_filter:
            command += ' -filter_complex '
            command += ' '.join(video_filter)

        if audio_filter and has_audio:
            command += ' -af '
            command_without_quote = ','.join(audio_filter)
            command += f'"{command_without_quote}"'
        elif audio_filter and not has_audio:
            command += silence_audio_command

        if other_command:
            command += ' '.join(other_command)

        if audio_codec and has_audio:
            command += f' {audio_codec} '
        elif audio_codec and not has_audio:
            command += silence_audio_command

        if video_codec:
            command += f' {video_codec} '

        command += f' "{output_video_path}"'
        return command


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

    f = FFmpegHandler()
    print(f.extract_audio_from_video(
            Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\b7bb97e21600b07f66c21e7932cb7550.mp4")))
    # print(f.reencode_video(Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\【111.mp4")))
    # f.extract_audio_from_video(video_input_path)
    # f.replace_video_audio(video_input_path,
    #                       Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\1\视频  (1)_out.wav"))
    # f.noisereduce(Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\1\视频  (3).mp4"),
    #               AudioNoiseReduction.STATIC)

    # f.merge_videos([Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\视频  (3).mp4"),
    #                        Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\视频  (3) - 副本.mp4")]
    #                )

    # print(f.encode_video_to_ts(Path(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\v\视频  (1).mp4")))
    app.exec()

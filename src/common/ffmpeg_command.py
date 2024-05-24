import os
import re
import subprocess
from pathlib import Path

import cv2
import loguru

from src.core.datacls import VideoScaling
from src.core.paths import FFMPEG_FILE
from src.signal_bus import SignalBus


class FFmpegCommand:
    def __init__(self):
        self._signal_bus: SignalBus = SignalBus()
        self.ffmpeg_bin: Path = FFMPEG_FILE

    def compress_video(self, input_file_path: Path | str, output_file_path: Path | str):
        input_file_path = Path(input_file_path)
        output_file_path = Path(output_file_path)
        if output_file_path.exists():
            output_file_path.unlink()
            loguru.logger.warning(f'已删除已存在的输出文件: {output_file_path}')
        cmd = f'"{self.ffmpeg_bin}" -y -hide_banner -i "{input_file_path}" -c:v libx264 -crf 23 -preset slow -qcomp 0.5 -psy-rd 0.3:0 -aq-mode 2 -aq-strength 0.8 -b:a 256k "{output_file_path}"'
        self._reset_progress("压缩视频")
        self._signal_bus.set_total_progress_max.emit(1)
        loguru.logger.debug('开始压缩视频')
        self._run_command(input_file_path, cmd)
        self._signal_bus.set_total_progress_finish.emit()
        loguru.logger.success(f'压缩视频完成,输出文件{output_file_path}')

    def audio_extract(self, input_video_path_list: list[VideoScaling], output_file_path: str | Path) -> Path:
        """
        通过ffmpeg提取视频文件中的音频，并将它们按照传入的顺序合并为单个音频文件。

        参数:
        input_video_path_list: 包含视频文件路径的列表。
        output_file_path: 合并后的音频输出路径。

        Returns:
        合并后的音频文件的路径
        """
        self._reset_progress("合并音频")
        loguru.logger.debug('开始提取音频')
        output_file_path = Path(output_file_path)

        # 生成临时文件路径列表，用于存储每个视频提取出的音频
        extracted_audios: list[Path] = [output_file_path.parent / f"temp_audio_{i}.mp3" for i, _ in
                enumerate(input_video_path_list)]
        self._signal_bus.set_total_progress_max.emit(len(extracted_audios))

        for each in extracted_audios:
            if each.exists():
                each.unlink()
                loguru.logger.warning(f'删除一个已经存在的音频文件{each.name}')

        # 提取每个视频文件中的音频
        for video_path, temp_audio in zip(input_video_path_list, extracted_audios):
            loguru.logger.debug(f'正在提取音频:{video_path.video_path}')
            video_path: VideoScaling
            cmd_extract = f'"{self.ffmpeg_bin}" -i "{video_path.video_path}" -q:a 0 -map a? {temp_audio}'
            self._run_command(video_path.video_path, cmd_extract)
            self._signal_bus.advance_total_progress.emit(1)

        # 修正音频速度
        # audio_changed_speed = [self.change_audio_speed(x.video_path, x.scale_rate) for x in input_video_path_list]
        # for temp_audio in extracted_audios:
        #     temp_audio.unlink()
        # extracted_audios = audio_changed_speed
        # loguru.logger.success('音频速度修正完成')

        # 生成ffmpeg合并命令中的输入文件列表部分
        inputs_concat = ' '.join([f'-i "{audio_path}"' for audio_path in extracted_audios])

        # ffmpeg的filter_complex选项用于合并音频
        filter_complex = f"concat=n={len(extracted_audios)}:v=0:a=1"

        # ffmpeg命令合并音频并输出到指定路径
        cmd_merge = f'"{self.ffmpeg_bin}" {inputs_concat} -filter_complex "{filter_complex}" -y {output_file_path}'
        if output_file_path.exists():
            output_file_path.unlink()
        # 需要彻底等待合并完成，否则会出现文件被占用的情况
        loguru.logger.debug(f'开始合并音频，输出文件: {output_file_path}')
        process = subprocess.run(cmd_merge, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 universal_newlines=True, encoding='utf-8', check=False)
        if process.returncode != 0:
            loguru.logger.error(f"FFmpeg命令运行失败: {cmd_merge}, 错误信息: {process.stderr}")
            raise subprocess.CalledProcessError(process.returncode, cmd_merge, output=process.stdout,
                                                stderr=process.stderr)
        loguru.logger.debug(f'音频合并完成，输出文件: {output_file_path}')

        # 完成合并后，删除临时音频文件
        for temp_audio in extracted_audios:
            loguru.logger.debug(f'正在删除文件{temp_audio}')
            temp_audio.unlink()

        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        loguru.logger.success(f'提取音频完成,输出文件: {output_file_path}')
        return output_file_path

    def change_audio_speed(self, audio_path: str | Path, scale_rate: float) -> Path:
        loguru.logger.debug(f'开始修正音频{audio_path}的速度, 缩放比例为{scale_rate}')
        audio_path = Path(audio_path)
        output_path = audio_path.parent / f'{audio_path.stem}_speed_changed.mp3'
        if output_path.exists():
            output_path.unlink()

        # Check if the file exists
        if not audio_path.exists():
            raise FileNotFoundError(f"The file {audio_path} does not exist.")

        # Check if the file is readable
        if not os.access(audio_path, os.R_OK):
            raise PermissionError(f"The file {audio_path} is not readable.")

        if scale_rate < 0.5 or scale_rate > 2:
            loguru.logger.critical(f'视频的缩放只能在0.5到2.0之间，当前的值为{scale_rate}')
            raise ValueError(f'视频的缩放只能在0.5到2.0之间，当前的值为{scale_rate}')

        # Construct the ffmpeg command
        cmd = f'"{self.ffmpeg_bin}" -y -i "{audio_path}" -filter:a "atempo={scale_rate}" "{output_path}"'

        # Run the command
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 shell=True, universal_newlines=True, encoding='utf-8', check=False)

        # Check the return code
        if process.returncode != 0:
            loguru.logger.error(f"FFmpeg命令运行失败: {cmd}, 错误信息: {process.stderr}")
            raise subprocess.CalledProcessError(process.returncode, cmd, output=process.stdout, stderr=process.stderr)
        loguru.logger.debug(f'音频速度修正完成，输出文件: {output_path}')

        return output_path

    def merge_video_with_audio(self, input_video_path: str | Path, input_audio_path: str | Path) -> Path:
        input_video_path = Path(input_video_path)
        input_audio_path = Path(input_audio_path)
        output_file_path = input_video_path.parent / f"{input_video_path.stem}_merged.mp4"
        if output_file_path.exists():
            output_file_path.unlink()
        cmd = f'"{self.ffmpeg_bin}" -y -hide_banner -i "{input_video_path}" -i "{input_audio_path}" -c:v copy -c:a aac -strict experimental "{output_file_path}" -y'
        self._reset_progress("合并音频")
        self._signal_bus.set_total_progress_max.emit(1)
        self._run_command(input_video_path, cmd)
        self._signal_bus.set_total_progress_finish.emit()
        loguru.logger.success(f'合并音频完成，输出文件: {output_file_path}')
        return output_file_path

    def copy_audio_to_video(self, video_with_audio: str | Path, video_without_audio: str | Path) -> Path:
        """将一个视频的音频拷贝到另一个视频"""
        video_with_audio = Path(video_with_audio)
        video_without_audio = Path(video_without_audio)
        output_file_path = video_without_audio.parent / f"{video_without_audio.stem}_with_audio.mp4"
        if output_file_path.exists():
            output_file_path.unlink()
        cmd = f'"{self.ffmpeg_bin}" -y -hide_banner -i "{video_without_audio}" -i "{video_with_audio}" -c:v copy -c:a aac -strict experimental "{output_file_path}"'
        self._reset_progress("合并音频")
        self._signal_bus.set_total_progress_max.emit(1)
        self._run_command(video_without_audio, cmd)
        self._signal_bus.set_total_progress_finish.emit()
        loguru.logger.success(f'合并音频完成，输出文件: {output_file_path}')
        return output_file_path

    def run(self):
        input_file = "input.mp4"
        output_file = "output.mp4"

        # 控制标志
        light_flow_enable = False
        has_crop = False
        has_rotate = True
        has_scale = True
        has_noise_reduction = True  # 降噪控制标志
        has_audio_normalization = True  # 音频标准化控制标志
        # 其他控制标志如视频平滑、稳定、修复等...

        frame_rate = "60"
        filters = []

        # 帧率调整
        if light_flow_enable:
            filters.append(
                "[0:v]scale=-2:-2[v];[v]minterpolate='mi_mode=mci:mc_mode=aobmc:me_mode=bidir:mb_size=16:vsbmc=1:fps={frame_rate}'")
        else:
            filters.append(f"fps=fps={frame_rate}")

        # 视频剪裁
        if has_crop:
            crop_x = "xxxx"  # 加入具体的参数值
            crop_y = "yyyy"
            crop_width = "wwww"
            crop_height = "hhhh"
            filters.append(f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y}")

        # 视频旋转
        if has_rotate:
            rotate_angle = "PLACEHOLDER_ROTATE_ANGLE"
            filters.append(f"rotate={rotate_angle}*PI/180")

        # 视频缩放
        if has_scale:
            scale_width = "1920"
            scale_height = "1080"
            filters.append(f"scale={scale_width}:{scale_height}:force_original_aspect_ratio=decrease")
            filters.append(f"pad={scale_width}:{scale_height}:(ow-iw)/2:(oh-ih)/2:black")

        # 构建FFmpeg命令
        commands = [
                "ffmpeg",
                "-i", input_file,
                ]

        # 添加帧率调整到命令
        if not light_flow_enable:
            commands += ["-r", frame_rate]

        # 过滤器链
        if filters:
            filter_chain = ",".join(filters)
            commands += ["-filter_complex", filter_chain]

        # 降噪处理
        if has_noise_reduction:
            pass  # 假设降噪滤镜已在 filters 列表中指定
        # 音频标准化
        audio_filters = []
        if has_audio_normalization:
            audio_filters.append("loudnorm=i=-24.0:lra=7.0:tp=-2.0:")

        # 将音频滤镜加入命令
        if audio_filters:
            audio_filter_chain = ",".join(audio_filters)
            commands += ["-af", audio_filter_chain]

        # 添加编码参数到命令
        commands += [
                "-map", "0:v",
                "-map", "0:a?",
                "-c:v", "libx264",
                "-crf", "23",
                "-preset", "slow",
                # 音频标准化后不需要这里再拷贝视频编码
                "-b:a", "256k",
                "-max_muxing_queue_size", "1024",
                output_file
                ]

        # 生成最终命令字符串
        final_command = ' '.join(commands)

    def _reset_progress(self, total_progress_desc: str):
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_description.emit(total_progress_desc)

    def _run_command(self, input_file_path: str | Path, command: str):
        # Convert input_file_path to a Path object
        input_file_path = Path(input_file_path)

        # Check if the file exists
        if not input_file_path.exists():
            raise FileNotFoundError(f"The file {input_file_path} does not exist.")

        # Check if the file is readable
        if not os.access(input_file_path, os.R_OK):
            raise PermissionError(f"The file {input_file_path} is not readable.")

        # 获取视频的总帧数
        cap = cv2.VideoCapture(str(input_file_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._signal_bus.set_detail_progress_max.emit(total_frames)
        cap.release()

        # 运行ffmpeg命令
        process = subprocess.Popen(command, shell=True,
                                   universal_newlines=True, encoding='utf-8')

        # # 运行ffmpeg命令
        # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        #                            universal_newlines=True, encoding='utf-8')
        #
        # # 更新进度条
        # for line in iter(process.stdout.readline, ''):
        #     if match := re.search(r'frame=\s*(\d+)', line):
        #         current_frame = int(match[1])
        #         self._signal_bus.set_detail_progress_current.emit(current_frame)
        #         if current_frame >= total_frames:
        #             break

        # 等待子进程完成并读取所有剩余的输出
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            loguru.logger.critical(f"FFmpeg命令运行失败: {command}, 错误信息: {stderr}")
            raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

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
    # ffmpeg_command.change_audio_speed(r"D:\Temp\audio.mp3", 0.5)



if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    test_ffmpeg_command()
    print('finished')
    app.exec()

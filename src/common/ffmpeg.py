import os
import re
import subprocess
from pathlib import Path

import cv2
import loguru

from src.config import (AudioNoiseReduction, AudioNormalization, FrameRateAdjustment, ScalingQuality, VideoCodec,
                        VideoNoiseReduction, cfg)
from src.core.datacls import CropInfo
from src.signal_bus import SignalBus

signal_bus = SignalBus()


def generate_ffmpeg_command(input_file: str | Path,
                            output_file_path: str | Path,
                            crop_position: CropInfo | None,
                            width: int,
                            height: int,
                            rotation_angle: int,
                            ) -> str:
    if rotation_angle not in {0, 90, 180, 270}:
        raise ValueError(f"rotation_angle must be one of 0, 90, 180, 270, current value is {rotation_angle}")

    input_file = str(input_file)
    frame_rate_adjustment_type = cfg.get(cfg.rate_adjustment_type)
    framerate = cfg.get(cfg.video_fps)
    video_noise_reduction: VideoNoiseReduction = cfg.get(cfg.video_noise_reduction)
    audio_noise_reduction: AudioNoiseReduction = cfg.get(cfg.audio_noise_reduction)
    audio_normalization: AudioNormalization = cfg.get(cfg.audio_normalization)
    has_shake = cfg.get(cfg.shake)
    deband: bool = cfg.get(cfg.deband)
    output_codec: VideoCodec = cfg.get(cfg.output_codec).value
    target_resolution = f"{width}:{height}"
    ffmpeg_path = cfg.get(cfg.ffmpeg_file)
    scaling_quality: ScalingQuality = cfg.get(cfg.scaling_quality)

    filters = []

    if frame_rate_adjustment_type == FrameRateAdjustment.NORMAL:
        filters.append(f"fps=fps={framerate}")
    elif frame_rate_adjustment_type == FrameRateAdjustment.MOTION_INTERPOLATION:
        filters.append(f"minterpolate='mi_mode=mci:mc_mode=aobmc:me_mode=bidir:mb_size=16:vsbmc=1:fps={framerate}'")

    if video_noise_reduction != VideoNoiseReduction.DISABLE:
        filters.append(video_noise_reduction.value)

    if has_shake:
        filters.append("deshake")

    if deband:
        filters.append("deband")

    if crop_position:
        filters.append(f"crop={crop_position.w}:{crop_position.h}:{crop_position.x}:{crop_position.y}")

    if rotation_angle == 180:
        filters.append("transpose=2,transpose=2")

    elif rotation_angle in {90, 270}:
        filters.append(f"transpose={2 if rotation_angle == 270 else 1}")

    # 缩放
    filters.append(
            f"scale={target_resolution}:flags={scaling_quality.value}:force_original_aspect_ratio=decrease,pad={target_resolution}:(ow-iw)/2:(oh-ih)/2:black")

    audio_filters = []
    # 音频标准化
    if audio_normalization != AudioNormalization.DISABLE:
        audio_filters.append(audio_normalization.value)

    # 音频降噪
    if audio_noise_reduction != AudioNoiseReduction.DISABLE:
        audio_filters.append(audio_noise_reduction.value.replace("\\", "/"))

    video_filter_chain = ','.join(filters)
    command = f'"{ffmpeg_path}" -i "{input_file}" -filter_complex "{video_filter_chain}"'
    if audio_filters:
        audio_filter_chain = ','.join(audio_filters)

        command += f" -af \"{audio_filter_chain}\""
    command += f' {output_codec} "{output_file_path}"'
    command += ' -y'
    loguru.logger.debug(f"FFmpeg命令: {command}")
    return command


def merge_videos(video_list: list[str | Path], output_path: str | Path):
    def convert_to_ts(input_file: str | Path, output_file: str | Path):
        loguru.logger.debug(f'正在将视频{input_file}转换为TS格式')
        ffmpeg_exe: Path = cfg.get(cfg.ffmpeg_file)
        command = f'"{ffmpeg_exe}" -fflags +genpts -i "{input_file}" -c copy -bsf:v h264_mp4toannexb -f mpegts "{output_file}" -y'
        run_command(input_file, command)

    def merge_ts_files(ts_files: list[str | Path], output_file: str | Path):
        loguru.logger.debug(f'正在将{ts_files}TS文件合并至->{output_file}')
        ffmpeg_exe: Path = cfg.get(cfg.ffmpeg_file)
        input_files = '|'.join(str(file) for file in ts_files)
        command = f'"{ffmpeg_exe}" -i "concat:{input_files}" -c copy -bsf:a aac_adtstoasc -vsync 2 "{output_file}" -y'
        run_command_without_progress(command)

    temp_dir: Path = Path(cfg.get(cfg.temp_dir))
    ts_files = []

    # Convert each video to TS format and store the paths in ts_files
    ts_dir = temp_dir / 'ts_files'
    if not ts_dir.exists():
        ts_dir.mkdir(parents=True, exist_ok=True)
        loguru.logger.debug(f'创建临时目录{ts_dir}成功')

    for video in video_list:
        ts_file = ts_dir / f'{Path(video).stem}.ts'
        convert_to_ts(video, ts_file)
        ts_files.append(ts_file)

    # Merge the TS files
    merge_ts_files(ts_files, output_path)


def run_command(input_file_path: str | Path, command: str):
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
    signal_bus.set_detail_progress_max.emit(total_frames)
    cap.release()

    # 运行ffmpeg命令
    # process = subprocess.Popen(command, shell=True,
    #                            universal_newlines=True, encoding='utf-8')

    # 运行ffmpeg命令
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True, encoding='utf-8')

    # 更新进度条
    for line in iter(process.stdout.readline, ''):
        loguru.logger.debug(line.strip())
        if match := re.search(r'frame=\s*(\d+)', line):
            current_frame = int(match[1])
            signal_bus.set_detail_progress_current.emit(current_frame)
            if current_frame >= total_frames:
                break

    # 等待子进程完成并读取所有剩余的输出
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        loguru.logger.critical(f"FFmpeg命令运行失败: {command}, 错误信息: {stderr}")
        raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

    # 终止子进程
    process.kill()
    signal_bus.set_detail_progress_finish.emit()


def run_command_without_progress(command: str):
    # 运行ffmpeg命令
    # process = subprocess.Popen(command, shell=True,
    #                            universal_newlines=True, encoding='utf-8')

    # 运行ffmpeg命令
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True, encoding='utf-8')

    # 更新进度条
    for line in iter(process.stdout.readline, ''):
        loguru.logger.debug(line.strip())

    # 等待子进程完成并读取所有剩余的输出
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        loguru.logger.critical(f"FFmpeg命令运行失败: {command}, 错误信息: {stderr}")
        raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

    # 终止子进程
    process.kill()


if __name__ == '__main__':
    input_file = r"E:\load\python\Project\VideoFusion\测试\video\video_2024-03-04_16-55-16.mp4"
    output_file = r"E:\load\python\Project\VideoFusion\测试\video\output3.mp4"
    print(generate_ffmpeg_command(input_file=Path(input_file),
                                  output_file_path=Path(output_file),
                                  crop_position=CropInfo(0, 0, 1920, 1080),
                                  width=1920,
                                  height=1080,
                                  rotation_angle=0))
    # video_list = Path(r"E:\load\python\Project\VideoMosaic\测试\video\2.txt").read_text(
    #         encoding="utf-8").replace('"', '').splitlines()
    # merge_videos(video_list,
    #              r"E:\load\python\Project\VideoMosaic\测试\video\output1.mp4")

import os
import re
import subprocess
from pathlib import Path

import cv2
import loguru

from src.config import FrameRateAdjustment, ScalingQuality, VideoCodec, cfg
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
    has_noise_reduction = cfg.get(cfg.noise_reduction)
    has_audio_normalization = cfg.get(cfg.audio_normalization)
    has_shake = cfg.get(cfg.shake)
    output_codec: VideoCodec = cfg.get(cfg.output_codec).value
    target_resolution = f"{width}:{height}"
    ffmpeg_path = cfg.get(cfg.ffmpeg_file)
    scaling_quality: ScalingQuality = cfg.get(cfg.scaling_quality)

    filters = []

    if frame_rate_adjustment_type == FrameRateAdjustment.NORMAL:
        filters.append(f"fps=fps={framerate}")
    elif frame_rate_adjustment_type == FrameRateAdjustment.MOTION_INTERPOLATION:
        filters.append(f"minterpolate='mi_mode=mci:mc_mode=aobmc:me_mode=bidir:mb_size=16:vsbmc=1:fps={framerate}'")

    if has_noise_reduction:
        filters.append("hqdn3d")

    if has_shake:
        filters.append("deshake")

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
    if has_audio_normalization:
        audio_filters.append("loudnorm=i=-24.0:lra=7.0:tp=-2.0:")

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
    # Convert output_path to a Path object
    loguru.logger.debug(f'视频输出路径为:{output_path}, 视频列表为:{video_list}')
    output_path = Path(output_path)
    temp_dir: Path = Path(cfg.get(cfg.temp_dir))
    video_merge_txt = temp_dir / 'video_merge.txt'
    video_merge_txt.touch(exist_ok=True)
    loguru.logger.debug(f'正在创建视频合并文件列表txt: {video_merge_txt}')

    # Create fileList.txt
    with open(video_merge_txt, 'w') as f:
        for video in video_list:
            f.write(f"file '{video}'\n")
    loguru.logger.debug(f'视频合并文件列表: {video_merge_txt}')
    ffmpeg_exe: Path = cfg.get(cfg.ffmpeg_file)
    ffmpeg_command = f'"{ffmpeg_exe}" -y -hide_banner -vsync 0 -safe 0 -f concat -i {video_merge_txt} -c:v copy -af aresample=async=1 "{output_path}"'

    # 运行ffmpeg命令
    process = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True, encoding='utf-8')

    # 读取并记录stdout和stderr
    for line in iter(process.stdout.readline, ''):
        loguru.logger.debug(line.strip())

    # 等待子进程完成
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        loguru.logger.critical(f"FFmpeg命令运行失败: {ffmpeg_command}, 错误信息: {stderr}")
        raise subprocess.CalledProcessError(process.returncode, ffmpeg_command, output=stdout, stderr=stderr)

    # 终止子进程
    process.kill()

    # subprocess.run(ffmpeg_command, shell=True, encoding='utf-8', universal_newlines=True)
    loguru.logger.success(f"视频合并完成, 输出文件: {output_path}")


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


if __name__ == '__main__':
    print(generate_ffmpeg_command(input_file=Path('test.mp4'),
                                  output_file_path=Path('output.mp4'),
                                  crop_position=CropInfo(0, 0, 1920, 1080),
                                  width=1920,
                                  height=1080,
                                  rotation_angle=0))

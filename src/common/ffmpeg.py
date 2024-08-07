import re
import subprocess
from pathlib import Path

import cv2
import loguru

from src.config import (AudioNoiseReduction, AudioNormalization, FrameRateAdjustment, ScalingQuality, VideoCodec,
                        VideoNoiseReduction, cfg)
from src.core.datacls import CropInfo
from src.signal_bus import SignalBus
from src.utils import TempDir, check_file_readability

signal_bus = SignalBus()


def generate_ffmpeg_command(input_file: str | Path,
                            output_file_path: str | Path,
                            crop_position: CropInfo | None,
                            target_width: int,
                            target_height: int,
                            audio_sample_rate: int,
                            rotation_angle: int,
                            ) -> str:
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
    deblock: bool = cfg.get(cfg.deblock)
    output_codec: VideoCodec = cfg.get(cfg.output_codec).value
    ffmpeg_path = cfg.get(cfg.ffmpeg_file)
    scaling_quality: ScalingQuality = cfg.get(cfg.scaling_quality)
    is_merging: bool = cfg.get(cfg.merge_video)

    filters = []

    if frame_rate_adjustment_type == FrameRateAdjustment.Normal:
        filters.append(f"fps=fps={framerate}")
    elif frame_rate_adjustment_type == FrameRateAdjustment.MotionInterpolation:
        filters.append(f"minterpolate='mi_mode=mci:mc_mode=aobmc:me_mode=bidir:mb_size=16:vsbmc=1:fps={framerate}'")

    if video_noise_reduction != VideoNoiseReduction.Disable:
        filters.append(video_noise_reduction.value)

    if has_shake:
        filters.append("deshake")

    if deband:
        filters.append("deband")

    if deblock:
        filters.append("deblock=alpha=1:beta=1")

    if crop_position:
        filters.append(f"crop={crop_position.w}:{crop_position.h}:{crop_position.x}:{crop_position.y}")

    if rotation_angle == 180:
        filters.append("transpose=2,transpose=2")

    elif rotation_angle in {90, 270}:
        filters.append(f"transpose={2 if rotation_angle == 270 else 1}")

    # 缩放(如果剪裁之后的视频分辨率和目标分辨率不一致则需要进行缩放,同时还需要处于合并状态,否则只剪裁不缩放)
    if crop_position and (crop_position.w != target_width and crop_position.h != target_height) and is_merging:
        new_width, new_height, pad_top, pad_bottom, pad_left, pad_right = calculate_dimensions(crop_position.w,
                                                                                               crop_position.h,
                                                                                               target_width,
                                                                                               target_height)
        # ffmpeg不允许scale大于pad,所以需要减1确保不会报错
        if new_width >= target_width:
            new_width -= 1
        if new_height >= target_height:
            new_height -= 1
        filters.append(
                f"scale={new_width}:{new_height}:flags={scaling_quality.value}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:{pad_left}:{pad_top}:black")

    audio_filters = []
    # 音频标准化
    if audio_normalization != AudioNormalization.Disable:
        audio_filters.append(audio_normalization.value)

    # 音频降噪
    if audio_noise_reduction != AudioNoiseReduction.Disable:
        audio_filters.append(audio_noise_reduction.value.replace("\\", "/"))

    # 音频重新采样
    audio_filters.append(f"aresample={audio_sample_rate}:resampler=soxr:precision=28:osf=s16:dither_method=triangular")

    video_filter_chain = ','.join(filters)
    command = f'"{ffmpeg_path}" -i "{input_file}" -filter_complex "{video_filter_chain}"'
    if audio_filters:
        audio_filter_chain = ','.join(audio_filters)

        command += f" -af \"{audio_filter_chain}\""

    # 音频同步以及重新编码
    command += f' -c:a aac -b:a {audio_sample_rate} -strict experimental -vsync 1'
    command += f' {output_codec} "{output_file_path}"'
    command += ' -y'
    loguru.logger.debug(f"FFmpeg命令: {command}")
    return command


def merge_videos(video_list: list[Path], output_path: Path):
    temp_dir: Path = TempDir().get_temp_dir()
    ffmpeg_exe: Path = cfg.get(cfg.ffmpeg_file)

    def convert_to_ts(input_file: Path, output_file: Path):
        # 创建一个临时的文本文件
        txt_path: Path = temp_dir / 'ts_videos.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            for video in video_list:
                f.write(f"file '{video}'\n")

        loguru.logger.debug(f'正在将视频{input_file}转换为TS格式')

        command = f'"{ffmpeg_exe}" -fflags +genpts -i "{input_file}" -c copy -bsf:v h264_mp4toannexb -vsync 2 -f mpegts "{output_file}" -y'
        run_command(input_file, command)

    def merge_ts_files(ts_files: list[Path], output_file: Path):
        loguru.logger.debug(f'正在将{ts_files}TS文件合并至->{output_file}')
        signal_bus.set_total_progress_description.emit("合并TS")
        signal_bus.set_total_progress_reset.emit()

        # 创建一个临时的文本文件
        txt_path: Path = temp_dir / 'ts_merge_videos.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            for video in ts_files:
                f.write(f"file '{video}'\n")

        command = f'"{ffmpeg_exe}" -fflags +genpts -f concat -safe 0 -i "{txt_path}" -c copy -bsf:a aac_adtstoasc -vsync 2 "{output_file}" -y'
        run_command_without_progress(command)

    # Convert each video to TS format and store the paths in ts_files
    ts_files = []
    ts_dir = temp_dir / 'ts_files'
    if not ts_dir.exists():
        ts_dir.mkdir(parents=True, exist_ok=True)
        loguru.logger.debug(f'创建临时目录{ts_dir}成功')

    # 将视频转换为TS格式
    signal_bus.set_detail_progress_reset.emit()
    signal_bus.set_total_progress_reset.emit()
    signal_bus.set_total_progress_max.emit(len(video_list))
    signal_bus.set_total_progress_description.emit("转为TS")
    for video in video_list:
        ts_file = ts_dir / f'{Path(video).stem}.ts'
        convert_to_ts(video, ts_file)
        ts_files.append(ts_file)
        signal_bus.advance_total_progress.emit(1)

    # Merge the TS files
    merge_ts_files(ts_files, output_path)


def run_command(input_file_path: str | Path, command: str):
    # Convert input_file_path to a Path object
    input_file_path = Path(input_file_path).resolve()
    loguru.logger.debug(f'正在处理视频: {input_file_path}haha')

    # Check if the file
    if not input_file_path.exists():
        raise FileNotFoundError(f"The file {input_file_path} does not exist.")

    # Check if the file is readable
    if not check_file_readability(input_file_path):
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
        signal_bus.failed.emit()
        raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

    # 终止子进程
    process.kill()
    signal_bus.set_detail_progress_finish.emit()


def run_command_without_progress(command: str):
    # 将命令变成列表
    command = command.replace('"', '')
    # 运行ffmpeg命令
    # process = subprocess.Popen(command,shell=True,
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
        signal_bus.failed.emit()
        raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

    # 终止子进程
    process.kill()


if __name__ == '__main__':
    import os
    from src.core.paths import ROOT

    os.chdir(ROOT)
    signal_bus.set_detail_progress_current.connect(lambda x: print(f'detail_progress_current: {x}'))
    signal_bus.set_detail_progress_max.connect(lambda x: print(f'detail_progress_max: {x}'))

    input_file = r"E:\load\python\Project\VideoFusion\测试\video\video_2024-03-04_16-55-16.mp4"
    output_file = r"E:\load\python\Project\VideoFusion\测试\video\output3.mp4"
    cmd = generate_ffmpeg_command(input_file=Path(input_file),
                                  output_file_path=Path(output_file),
                                  crop_position=None,
                                  target_width=1920,
                                  target_height=1080,
                                  rotation_angle=0,
                                  audio_sample_rate=44100)
    print(cmd)
    run_command(input_file, cmd)

    # video_list = Path(r"E:\load\python\Project\VideoFusion\测试\video\1.txt").read_text(
    #         ).replace('"', '').splitlines()
    # merge_videos(video_list,
    #              r"E:\load\python\Project\VideoFusion\TempAndTest\output.mp4")

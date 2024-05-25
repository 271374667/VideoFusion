from enum import Enum
from pathlib import Path

from qfluentwidgets import (BoolValidator, ConfigItem, ConfigValidator, EnumSerializer, FolderValidator,
                            OptionsConfigItem, OptionsValidator, QConfig, RangeConfigItem, RangeValidator, qconfig)

from src.core.paths import (CONFIG_FILE, FFMPEG_FILE, OUTPUT_FILE, TEMP_DIR)

__version__ = "0.4.3"


# 补帧策略
class FrameRateAdjustment(Enum):
    NORMAL = 1
    MOTION_INTERPOLATION = 2


# 缩放质量
class ScalingQuality(Enum):
    FASTEST = 'nearest'
    MEDIUM = 'bilinear'
    BEST = 'lanczos'


# 视频编码策略
class VideoCodec(Enum):
    H264 = "-c:v libx264 -crf 23 -preset slow -qcomp 0.5 -psy-rd 0.3:0 -aq-mode 2 -aq-strength 0.8 -b:a 256k"
    H264Intel = "-c:v h264_qsv -qscale 15 -b:a 256k"
    H264AMD = "-c:v h264_amf -qscale 15 -b:a 256k"
    H264Nvidia = "-c:v h264_nvenc -qscale 15 -b:a 256k"
    H265 = "-c:v libx265 -crf 28 -b:a 256k"
    H265Intel = "-c:v hevc_qsv -qscale 15 -b:a 256k"
    H265AMD = "-c:v hevc_amf -qscale 15 -b:a 256k"
    H265Nvidia = "-c:v hevc_nvenc -qscale 15 -b:a 256k"


# 预览视频帧
class PreviewFrame(Enum):
    FirstFrame = 1
    LastFrame = 2
    RandomFrame = 3


class OutputFileValidator(ConfigValidator):
    """ Config validator """

    def validate(self, value):
        """ Verify whether the value is legal """
        file_path: Path = Path(value)
        return bool(file_path.is_file())

    def correct(self, value):
        """ correct illegal value """
        file_path: Path = Path(value)
        return value if file_path.is_file() else str(OUTPUT_FILE)


class FFmpegValidator(ConfigValidator):
    """ Config validator """

    def validate(self, value):
        """ Verify whether the value is legal """
        ffmpeg_path: Path = Path(value)
        return bool(ffmpeg_path.is_file() and ffmpeg_path.suffix == '.exe')

    def correct(self, value):
        """ correct illegal value """
        ffmpeg_path: Path = Path(value)
        if ffmpeg_path.is_file() and ffmpeg_path.suffix == '.exe':
            return value
        return str(FFMPEG_FILE)


class Config(QConfig):
    # 视频质量
    output_file_path = ConfigItem("Video", "输出文件路径", str(OUTPUT_FILE), OutputFileValidator())
    noise_reduction = ConfigItem("Video", "视频降噪", True, BoolValidator())
    audio_normalization = ConfigItem("Video", "音频响度标准化", False, BoolValidator())
    shake = ConfigItem("Video", "视频去抖动", False, BoolValidator())
    video_fps = RangeConfigItem("Video", "目标视频帧率", 30, RangeValidator(1, 144))
    video_sample_rate = RangeConfigItem("Video", "黑边采样率", 5, RangeValidator(0, 10))
    scaling_quality = OptionsConfigItem("Video", "缩放质量", ScalingQuality.BEST, OptionsValidator(ScalingQuality),
                                        EnumSerializer(ScalingQuality))
    rate_adjustment_type = OptionsConfigItem("Video", "补帧策略", FrameRateAdjustment.NORMAL,
                                             OptionsValidator(FrameRateAdjustment), EnumSerializer(FrameRateAdjustment))
    output_codec = OptionsConfigItem("Video", "输出编码策略", VideoCodec.H264, OptionsValidator(VideoCodec),
                                     EnumSerializer(VideoCodec))

    # 全局设置
    ffmpeg_file = ConfigItem("General", "FFmpeg路径", str(FFMPEG_FILE), FFmpegValidator())
    temp_dir = ConfigItem("General", "临时目录", str(TEMP_DIR), FolderValidator())
    delete_temp_dir = ConfigItem("General", "完成后删除临时目录", True, BoolValidator())
    preview_video_remove_black = ConfigItem("General", "预览视频是否去黑边", False, BoolValidator())
    preview_frame = OptionsConfigItem("General", "预览视频帧", PreviewFrame.FirstFrame, OptionsValidator(PreviewFrame),
                                      EnumSerializer(PreviewFrame))
    preview_auto_play = ConfigItem("General", "预览视频自动播放", False, BoolValidator())


cfg = Config()
cfg.file = CONFIG_FILE
if not CONFIG_FILE.exists():
    cfg.save()
qconfig.load(CONFIG_FILE, cfg)

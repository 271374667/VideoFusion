from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True, slots=True)
class VideoInfo:
    video_path: Path
    fps: int
    frame_count: int
    width: int
    height: int
    crop: Optional["CropInfo"] = None


@dataclass(frozen=True, slots=True)
class CropInfo:
    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True, slots=True)
class VideoScaling:
    video_path: Path
    scale_rate: float  # 音频长度缩放比例


@dataclass(frozen=True, slots=True)
class FFmpegDTO:
    video_info: VideoInfo
    ffmpeg_command: str | None = None

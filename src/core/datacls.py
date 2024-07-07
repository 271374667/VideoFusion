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
    audio_sample_rate: int  # 音频采样率,例如44100
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

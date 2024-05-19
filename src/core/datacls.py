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

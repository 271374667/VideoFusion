from typing import Literal

import cv2
import numpy as np

from src.core.datacls import CropInfo
from src.utils import calculate_dimensions


def crop_video(frame: np.ndarray, crop_info: CropInfo) -> np.ndarray:
    return frame[crop_info.y:crop_info.y + crop_info.h, crop_info.x:crop_info.x + crop_info.w]


def rotation_video(frame: np.ndarray, angle: Literal[90, 180, 270]) -> np.ndarray:
    match angle:
        case 90:
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        case 180:
            return cv2.rotate(frame, cv2.ROTATE_180)
        case 270:
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        case _:
            raise ValueError('angle must be 90, 180 or 270')


def resize_video(frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
    current_width = frame.shape[1]
    current_height = frame.shape[0]
    new_width, new_height, pad_top, pad_bottom, pad_left, pad_right = calculate_dimensions(current_width,
                                                                                           current_height, target_width,
                                                                                           target_height)
    frame = cv2.resize(frame, (new_width, new_height))
    frame = cv2.copyMakeBorder(frame, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT,
                               value=[0, 0, 0])
    return frame

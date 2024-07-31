from pathlib import Path

import cv2

from src.common.black_remove_algorithm.black_remove_algorithm import BlackRemoveAlgorithm
from src.common.black_remove_algorithm.img_black_remover import IMGBlackRemover
from src.core.datacls import CropInfo, VideoInfo


class VideoInfoReader:
    def __init__(self, video_path: str):
        self.video_path = Path(video_path)

    def get_video_info(self, black_remove_algorithm: BlackRemoveAlgorithm | None) -> VideoInfo:
        video = cv2.VideoCapture(str(self.video_path))
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(video.get(cv2.CAP_PROP_FPS))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.release()

        if black_remove_algorithm is None:
            return VideoInfo(video_path=self.video_path,
                             fps=fps,
                             frame_count=frame_count,
                             width=width,
                             height=height)

        # 获取剪裁信息
        x, y, w, h = black_remove_algorithm.remove_black(self.video_path)
        if w == width and h == height:
            return VideoInfo(video_path=self.video_path,
                             fps=fps,
                             frame_count=frame_count,
                             width=width,
                             height=height)
        elif x == 0 and y == 0 and w == 0 and h == 0:
            return VideoInfo(video_path=self.video_path,
                             fps=fps,
                             frame_count=frame_count,
                             width=width,
                             height=height)
        return VideoInfo(video_path=self.video_path,
                         fps=fps,
                         frame_count=frame_count,
                         width=width,
                         height=height,
                         crop=CropInfo(x, y, w, h))

    def get_crop_info(self, black_remove_algorithm: BlackRemoveAlgorithm) -> CropInfo:
        x, y, w, h = black_remove_algorithm.remove_black(self.video_path)
        return CropInfo(x, y, w, h)


if __name__ == '__main__':
    v = VideoInfoReader(r"E:\load\python\Project\VideoFusion\tests\test_data\videos\001.mp4")
    print(v.get_video_info(IMGBlackRemover()))

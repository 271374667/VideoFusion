from src.common.processors.opencv_processors.opencv_processor_manager import OpenCVProcessorManager
from src.common.video_info_reader import VideoInfoReader


class ProgramCoordinator:
    def __init__(self):
        # 先获取视频信息
        self._video_info_reader = VideoInfoReader()

        self._opencv_processor_manager = OpenCVProcessorManager()

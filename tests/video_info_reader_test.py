import unittest
from pathlib import Path

from src.common.black_remove_algorithm.video_remover import VideoRemover
from src.common.video_info_reader import VideoInfoReader

TEST_VIDEO_PATH: Path = Path(r"E:\load\python\Project\VideoFusion\tests\test_data\videos\001.mp4")


class TestVideoInfoReader(unittest.TestCase):
    def test_get_video_info(self):
        # Assuming there's a test video at the specified path with known properties
        test_video_path = TEST_VIDEO_PATH
        expected_fps = 59
        expected_frame_count = 1057
        expected_width = 720
        expected_height = 1610
        expected_audio_sample_rate = 44100
        crop = (0, 513, 720, 490)

        reader = VideoInfoReader(str(test_video_path))
        video_info = reader.get_video_info(VideoRemover())

        self.assertEqual(video_info.fps, expected_fps)
        self.assertEqual(video_info.frame_count, expected_frame_count)
        self.assertEqual(video_info.width, expected_width)
        self.assertEqual(video_info.height, expected_height)
        self.assertEqual(video_info.audio_sample_rate, expected_audio_sample_rate)
        self.assertEqual((video_info.crop.x, video_info.crop.y, video_info.crop.w, video_info.crop.h), crop)


if __name__ == '__main__':
    unittest.main()

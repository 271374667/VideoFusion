import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.common.black_remove_algorithm.img_black_remover import IMGBlackRemover

VIDEO_PATH: Path = Path(r"E:\load\python\Project\VideoFusion\tests\test_data\videos\001.mp4")


class IMGBlackRemoverTests(unittest.TestCase):

    def setUp(self):
        self.img_black_remover = IMGBlackRemover()

    @patch('cv2.VideoCapture')
    @patch('pathlib.Path.exists', return_value=True)
    def video_file_is_supported_and_exists_returns_coordinates(self, mock_exists, mock_VideoCapture):
        mock_video = MagicMock()
        mock_video.get.side_effect = [100, 1920, 1080]  # Mock total_frames, width, height
        mock_VideoCapture.return_value = mock_video
        expected = (0, 0, 1920, 1080)  # Assuming the video has no black borders

        result = self.img_black_remover.remove_black(VIDEO_PATH)

        self.assertEqual(result, expected)

    @patch('pathlib.Path.exists', return_value=False)
    def video_file_does_not_exist_raises_FileNotFoundError(self, mock_exists):
        with self.assertRaises(FileNotFoundError):
            self.img_black_remover.remove_black(VIDEO_PATH)

    def video_file_has_unsupported_extension_raises_ValueError(self):
        with self.assertRaises(ValueError):
            self.img_black_remover.remove_black("unsupported_file.txt")

    @patch('cv2.VideoCapture')
    @patch('pathlib.Path.exists', return_value=True)
    def video_file_with_black_borders_returns_correct_coordinates(self, mock_exists, mock_VideoCapture):
        mock_video = MagicMock()
        mock_video.get.side_effect = [100, 1920, 1080]  # Mock total_frames, width, height
        mock_VideoCapture.return_value = mock_video
        # Assuming the video has black borders and the main content is centered with 100px padding
        expected = (100, 100, 1720, 880)

        result = self.img_black_remover.remove_black(VIDEO_PATH)

        self.assertEqual(result, expected)

    @patch('cv2.VideoCapture')
    @patch('pathlib.Path.exists', return_value=True)
    def video_file_with_no_frames_raises_RuntimeError(self, mock_exists, mock_VideoCapture):
        mock_video = MagicMock()
        mock_video.get.side_effect = [0, 1920, 1080]  # Mock total_frames as 0
        mock_VideoCapture.return_value = mock_video

        with self.assertRaises(RuntimeError):
            self.img_black_remover.remove_black(VIDEO_PATH)


if __name__ == '__main__':
    unittest.main()

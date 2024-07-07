import unittest
from pathlib import Path
from unittest.mock import patch

from src.common.black_remove_algorithm.img_black_remover import IMGBlackRemover


class TestIMGBlackRemover(unittest.TestCase):

    def setUp(self):
        self.img_black_remover = IMGBlackRemover()

    @patch('src.common.utils.image_utils.ImageUtils.has_black_border', return_value=True)
    def test_video_with_black_borders_returns_correct_coordinates(self, mock_has_black_border):
        video_path = Path("E:\\load\\python\\Project\\VideoFusion\\tests\\test_data\\videos\\001.mp4")
        x, y, w, h = self.img_black_remover.remove_black(video_path)
        self.assertNotEqual((x, y, w, h), (0, 0, 0, 0),
                            "Should not return zero coordinates for a video with black borders")

        self.assertEqual((x, y, w, h), (0, 0, 720, 1610))

    @patch('src.common.utils.image_utils.ImageUtils.has_black_border', return_value=False)
    def test_video_without_black_borders_returns_full_frame(self, mock_has_black_border):
        video_path = Path("E:\\load\\python\\Project\\VideoFusion\\tests\\test_data\\videos\\002.mp4")
        x, y, w, h = self.img_black_remover.remove_black(video_path)
        self.assertEqual((x, y, w, h), (0, 0, 640, 480), "Should return full frame for a video without black borders")

    def test_invalid_video_format_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.img_black_remover.remove_black(
                    "E:\\load\\python\\Project\\VideoFusion\\tests\\test_data\\videos\\invalid_format.txt")

    def test_non_existent_video_raises_file_not_found_error(self):
        with self.assertRaises(FileNotFoundError):
            self.img_black_remover.remove_black(
                    "E:\\load\\python\\Project\\VideoFusion\\tests\\test_data\\videos\\non_existent.mp4")


if __name__ == '__main__':
    unittest.main()

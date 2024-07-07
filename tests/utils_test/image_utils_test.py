import unittest
from pathlib import Path

import numpy as np

from src.common.utils.image_utils import ImageUtils

has_black_img1: Path = Path(r"E:\load\python\Project\VideoFusion\tests\test_data\images\has_black_1.png")
has_black_img2: Path = Path(r"E:\load\python\Project\VideoFusion\tests\test_data\images\has_black_2.jpg")
no_black_img1: Path = Path(r"E:\load\python\Project\VideoFusion\tests\test_data\images\no_black_1.jpg")
no_black_img2: Path = Path(r"E:\load\python\Project\VideoFusion\tests\test_data\images\no_black_2.jpg")


class TestImageUtils(unittest.TestCase):
    def setUp(self):
        self.image_utils = ImageUtils()
        self.black_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.white_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        self.image_with_black_border = np.ones((100, 100, 3), dtype=np.uint8) * 255
        self.image_with_black_border[:5, :, :] = 0
        self.image_with_black_border[-5:, :, :] = 0
        self.image_with_black_border[:, :5, :] = 0
        self.image_with_black_border[:, -5:, :] = 0

    def test_is_black_true(self):
        self.assertTrue(self.image_utils.is_black(self.black_image))

        img1 = self.image_utils.read_image(has_black_img1)
        self.assertTrue(bool(self.image_utils.has_black_border(img1)))

    def test_has_black_border(self):
        self.assertTrue(self.image_utils.has_black_border(self.image_with_black_border))

        img1 = self.image_utils.read_image(has_black_img1)
        self.assertTrue(self.image_utils.has_black_border(img1))

        img2 = self.image_utils.read_image(has_black_img2)
        self.assertTrue(self.image_utils.has_black_border(img2))

        img3 = self.image_utils.read_image(no_black_img1)
        self.assertFalse(self.image_utils.has_black_border(img3))

        img4 = self.image_utils.read_image(no_black_img2)
        self.assertFalse(self.image_utils.has_black_border(img4))


if __name__ == '__main__':
    unittest.main()

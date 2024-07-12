import unittest
from unittest.mock import MagicMock

import numpy as np

from src.common.processors.opencv_processors.crop_processor import CropProcessor


class CropProcessorTest(unittest.TestCase):
    def setUp(self):
        self.processor = CropProcessor()
        self.processor.processor_global_var.get = MagicMock(side_effect=lambda key: {
                "crop_x": 10,
                "crop_y": 20,
                "crop_width": 100,
                "crop_height": 200
                }.get(key, None))
        self.frame = np.zeros((300, 300), dtype=np.uint8)

    def test_cropping_with_valid_parameters_returns_correctly_cropped_frame(self):
        cropped_frame = self.processor.process(self.frame)
        self.assertEqual(cropped_frame.shape, (200, 100))

    def test_cropping_with_one_parameter_missing_returns_original_frame(self):
        self.processor.crop_x = None  # Simulate missing parameter
        original_frame = self.frame.copy()
        cropped_frame = self.processor.process(self.frame)
        np.testing.assert_array_equal(cropped_frame, original_frame)

    def test_cropping_with_all_parameters_missing_returns_original_frame(self):
        self.processor.crop_x = None
        self.processor.crop_y = None
        self.processor.crop_width = None
        self.processor.crop_height = None
        original_frame = self.frame.copy()
        cropped_frame = self.processor.process(self.frame)
        np.testing.assert_array_equal(cropped_frame, original_frame)

    def test_cropping_outside_of_frame_bounds_returns_correctly_cropped_frame(self):
        # Adjust parameters to exceed frame bounds
        self.processor.crop_x = 250
        self.processor.crop_y = 250
        self.processor.crop_width = 100
        self.processor.crop_height = 100
        cropped_frame = self.processor.process(self.frame)
        self.assertTrue(cropped_frame.size > 0)  # Check if any cropping happened


if __name__ == '__main__':
    unittest.main()

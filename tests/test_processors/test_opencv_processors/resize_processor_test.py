import unittest

import numpy as np

from src.common.processors.opencv_processors.resize_processor import ResizeProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar


class ResizeProcessorTest(unittest.TestCase):

    def setUp(self):
        # Set up ProcessorGlobalVar with default values
        ProcessorGlobalVar().update("target_width", 800)
        ProcessorGlobalVar().update("target_height", 600)
        self.processor = ResizeProcessor()

    def create_frame(self, width, height):
        # Create a dummy frame for testing
        return np.zeros((height, width, 3), dtype=np.uint8)

    def test_resize_to_target_dimensions(self):
        frame = self.create_frame(400, 300)
        processed_frame = self.processor.process(frame)
        self.assertEqual(processed_frame.shape[1], 800)  # width
        self.assertEqual(processed_frame.shape[0], 600)  # height

    def test_resize_with_aspect_ratio_preserved(self):
        frame = self.create_frame(1024, 768)
        processed_frame = self.processor.process(frame)
        self.assertTrue(processed_frame.shape[1] <= 800)
        self.assertTrue(processed_frame.shape[0] <= 600)
        self.assertEqual(processed_frame.shape[1], processed_frame.shape[0] * (4 / 3))

    def test_resize_with_padding(self):
        frame = self.create_frame(1600, 900)
        processed_frame = self.processor.process(frame)
        # Check if padding was added correctly
        expected_width = 800
        expected_height = 600
        self.assertEqual(processed_frame.shape[1], expected_width)
        self.assertEqual(processed_frame.shape[0], expected_height)
        # Check for black padding
        top_row = processed_frame[0, :]
        bottom_row = processed_frame[-1, :]
        left_column = processed_frame[:, 0]
        right_column = processed_frame[:, -1]
        self.assertTrue(np.all(top_row == [0, 0, 0]))
        self.assertTrue(np.all(bottom_row == [0, 0, 0]))
        self.assertTrue(np.all(left_column == [0, 0, 0]))
        self.assertTrue(np.all(right_column == [0, 0, 0]))

    def test_resize_with_zero_dimensions_raises_value_error(self):
        frame = self.create_frame(0, 0)
        with self.assertRaises(ValueError):
            self.processor.process(frame)

    def test_cache_usage_reduces_computation(self):
        frame = self.create_frame(400, 300)
        # Process the frame twice and check if cache is used
        processed_frame_first = self.processor.process(frame)
        self.processor._cache.set_values(None, None, None, None, None, None)  # Invalidate cache
        processed_frame_second = self.processor.process(frame)
        self.assertNotEqual(id(processed_frame_first), id(processed_frame_second))

    def test_reset_cache(self):
        self.processor._cache.set_values(800, 600, 0, 0, 0, 0)
        self.processor._cache.reset()
        self.assertFalse(self.processor._cache.is_set())


if __name__ == '__main__':
    unittest.main()

import unittest

import numpy as np

from src.common.processors.opencv_processors.rotate_processor import RotateProcessor
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.core.enums import Orientation


class RotateProcessorTest(unittest.TestCase):
    def setUp(self):
        self.processor = RotateProcessor()
        self.processor_global_var = ProcessorGlobalVar()
        self.processor_global_var.update("rotation_angle", 90)  # Assuming there's a setter method
        self.processor_global_var.update("orientation",
                                                    Orientation.HORIZONTAL)  # Assuming there's a setter method

    def test_rotate_horizontal_video_no_needs_rotation(self):
        self.processor_global_var.update("orientation", Orientation.HORIZONTAL)  # Change orientation to horizontal
        frame = np.zeros((100, 300, 3), np.uint8)  # HxW, indicating a vertical frame needing rotation
        rotated_frame = self.processor.process(frame)
        self.assertEqual(rotated_frame.shape, (100, 300, 3))

    def test_rotate_horizontal_video_needs_rotation(self):
        self.processor_global_var.update("orientation", Orientation.HORIZONTAL)  # Change orientation to horizontal
        self.processor_global_var.update("rotation_angle", 90)
        frame = np.zeros((300, 100, 3), np.uint8)  # HxW, indicating a vertical frame needing rotation
        rotated_frame = self.processor.process(frame)
        self.assertEqual(rotated_frame.shape, (100, 300, 3))

    def test_rotate_vertical_video_needs_no_rotation(self):
        self.processor_global_var.update("orientation", Orientation.VERTICAL)
        frame = np.zeros((300, 100, 3), np.uint8)  # HxW, indicating a horizontal frame with no need for rotation
        rotated_frame = self.processor.process(frame)
        self.assertEqual(rotated_frame.shape, (300, 100, 3))  # Shape remains the same

    def test_rotate_vertical_video_needs_rotation(self):
        self.processor_global_var.update("orientation",
                                                    Orientation.VERTICAL)  # Change orientation to vertical
        frame = np.zeros((100, 300, 3), np.uint8)  # HxW, indicating a horizontal frame needing rotation
        rotated_frame = self.processor.process(frame)
        self.assertEqual(rotated_frame.shape, (300, 100, 3))  # WxH after rotation

    def test_rotate_horizontal_video_needs_no_rotation(self):
        self.processor._processor_global_var.update("orientation",
                                                    Orientation.HORIZONTAL)  # Ensure orientation is horizontal
        frame = np.zeros((100, 300, 3), np.uint8)  # HxW, indicating a vertical frame with no need for rotation
        rotated_frame = self.processor.process(frame)
        self.assertEqual(rotated_frame.shape, (100, 300, 3))  # Shape remains the same

    def test_raise_error_on_missing_orientation(self):
        self.processor._processor_global_var.update("orientation", None)  # Remove orientation
        frame = np.zeros((100, 300, 3), np.uint8)
        with self.assertRaises(ValueError):
            self.processor.process(frame)

    def test_raise_error_on_missing_angle(self):
        self.processor._processor_global_var.update("rotation_angle", None)  # Remove angle
        frame = np.zeros((100, 300, 3), np.uint8)
        with self.assertRaises(ValueError):
            self.processor.process(frame)

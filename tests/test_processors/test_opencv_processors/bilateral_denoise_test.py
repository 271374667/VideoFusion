import unittest

import numpy as np

from src.common.processors.opencv_processors.means_doising_processor import BilateralDenoiseProcessor


class TestBilateralDenoiseProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = BilateralDenoiseProcessor()

    def test_frame_with_uniform_noise_is_denoised(self):
        # Create a frame with uniform noise
        noisy_frame = np.random.uniform(0, 255, (100, 100, 3)).astype(np.uint8)
        # Process the frame
        denoised_frame = self.processor.process(noisy_frame)
        # Check if the denoised frame has less noise than the original
        self.assertTrue(np.var(denoised_frame) < np.var(noisy_frame))

    def test_frame_with_salt_and_pepper_noise_is_denoised(self):
        # Create a frame with salt and pepper noise
        noisy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        noisy_frame[np.random.choice([True, False], size=noisy_frame.shape)] = 255
        # Process the frame
        denoised_frame = self.processor.process(noisy_frame)
        # Check if the denoised frame has less noise than the original
        self.assertTrue(np.mean(denoised_frame) > np.mean(noisy_frame[np.where(noisy_frame == 0)]))
        self.assertTrue(np.mean(denoised_frame) < np.mean(noisy_frame[np.where(noisy_frame == 255)]))

    def test_empty_frame_returns_same_frame(self):
        # Create an empty frame
        empty_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Process the frame
        processed_frame = self.processor.process(empty_frame)
        # Check if the processed frame is the same as the input
        self.assertTrue(np.array_equal(processed_frame, empty_frame))


if __name__ == '__main__':
    unittest.main()

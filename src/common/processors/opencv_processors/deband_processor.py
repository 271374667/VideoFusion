import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor


class DebandProcessor(OpenCVProcessor):
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        使用opencv对输入的帧进行去色带处理

        Args:
            frame: 输入的帧

        Returns:
            去色带处理后的帧
        """

        # 给图像添加高斯噪声
        def add_gaussian_noise(frame, mean=0, sigma=10):
            noise = np.random.normal(mean, sigma, frame.shape).astype(np.float32)
            noisy_frame = cv2.add(frame.astype(np.float32), noise)
            noisy_frame = np.clip(noisy_frame, 0, 255).astype(np.uint8)
            return noisy_frame

        # 减少图像中的色带效应
        def reduce_color_banding(frame):
            noisy_frame = add_gaussian_noise(frame)
            # 使用高斯模糊平滑图像
            denoised_frame = cv2.GaussianBlur(noisy_frame, (5, 5), 0)
            return denoised_frame

        return reduce_color_banding(frame)


if __name__ == '__main__':
    img_path = r"E:\load\python\Project\VideoFusion\TempAndTest\images\deband1 (2).jpg"
    img = cv2.imread(img_path)
    cv2.imshow("img", img)
    if img is None:
        print(f"Failed to load image from {img_path}")
    else:
        deband_processor = DebandProcessor()
        result = deband_processor.process(img)
        cv2.imshow("result", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

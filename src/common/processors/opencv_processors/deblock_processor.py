import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor


class DeblockProcessor(OpenCVProcessor):
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        使用cv2.medianBlur对输入的帧进行去色块处理

        Args:
            frame: 输入的帧

        Returns:
            去色块处理后的帧
        """
        # 使用中值滤波去色块，这里的5是滤波器的大小
        return cv2.medianBlur(frame, 5)


if __name__ == '__main__':
    img_path = r"E:\load\python\Project\VideoFusion\TempAndTest\images\deband1 (2).jpg"
    img = cv2.imread(img_path)
    cv2.imshow("img", img)
    if img is None:
        print(f"Failed to load image from {img_path}")
    else:
        deband_processor = DeblockProcessor()
        result = deband_processor.process(img)
        cv2.imshow("result", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

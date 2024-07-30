import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor


class BrightnessContrastProcessor(OpenCVProcessor):
    def __init__(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        初始化自适应直方图均衡化处理器

        Args:
            clip_limit: 对比度限制
            tile_grid_size: 每个网格的大小
        """
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        对输入的帧进行亮度和对比度调整并返回处理后的帧

        Args:
            frame: 输入的帧

        Returns:
            处理后的帧
        """
        # Convert frame to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        # Split the LAB image to different channels
        l, a, b = cv2.split(lab)

        # Apply CLAHE to the L channel
        clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)
        cl = clahe.apply(l)

        # Merge the CLAHE enhanced L channel with the a and b channel
        limg = cv2.merge((cl, a, b))

        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)


# Example usage
if __name__ == "__main__":
    bc_processor = BrightnessContrastProcessor()
    origin_img = cv2.imread(r"E:\load\python\Project\VideoFusion\TempAndTest\dy\0002.jpg")
    enhanced_img = bc_processor.process(origin_img)
    origin_img = cv2.resize(origin_img, (480, 720))
    enhanced_img = cv2.resize(enhanced_img, (480, 720))
    cv2.imshow("origin_img", origin_img)
    cv2.imshow("enhanced_img", enhanced_img)
    # cap = cv2.VideoCapture(r"E:\load\python\Project\VideoFusion\测试\video\black.mp4")
    # out = cv2.VideoWriter(r"E:\load\python\Project\VideoFusion\测试\video\black_out.mp4", cv2.VideoWriter.fourcc(*'mp4v'), 30.0,
    #                       (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    #
    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if not ret:
    #         break
    #     enhanced_frame = bc_processor.process(frame)
    #     out.write(enhanced_frame)
    #
    # cap.release()
    # out.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()

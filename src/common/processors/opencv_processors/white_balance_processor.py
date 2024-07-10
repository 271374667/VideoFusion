import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor


class WhiteBalanceProcessor(OpenCVProcessor):
    def __init__(self):
        # Using the SimpleWB white balance algorithm
        self.white_balance = cv2.xphoto.createSimpleWB()

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        对输入的帧进行白平衡处理并返回处理后的帧

        Args:
            frame: 输入的帧

        Returns:
            处理后的帧
        """
        return self.white_balance.balanceWhite(frame)


# Example usage
if __name__ == "__main__":
    wb_processor = WhiteBalanceProcessor()
    cap = cv2.VideoCapture(r"E:\load\python\Project\VideoFusion\测试\video\001.mp4")
    out = cv2.VideoWriter(r"E:\load\python\Project\VideoFusion\测试\video\001_out.mp4", cv2.VideoWriter.fourcc(*'mp4v'), 30.0,
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        balanced_frame = wb_processor.process(frame)
        out.write(balanced_frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

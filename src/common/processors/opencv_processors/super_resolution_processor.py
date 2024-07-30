import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor
from src.core.paths import ESPCN_x2_FILE, LapSRN_x2_FILE


class SuperResolutionESPCNProcessor(OpenCVProcessor):
    def __init__(self, scale_factor=2):
        """
        图像超分辨率处理器，使用ESPCN模型
        """
        self.model = cv2.dnn_superres.DnnSuperResImpl_create()
        self.model.readModel(str(ESPCN_x2_FILE))
        self.scale_factor = scale_factor
        self.model.setModel("espcn", self.scale_factor)

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        对输入的帧进行超分辨率处理并返回处理后的帧，但保持原尺寸

        Args:
            frame: 输入的帧

        Returns:
            处理后的帧
        """
        # 获取原始尺寸
        original_size = (frame.shape[1], frame.shape[0])

        # 缩放输入帧
        scaled_size = (frame.shape[1] // self.scale_factor, frame.shape[0] // self.scale_factor)
        scaled_frame = cv2.resize(frame, scaled_size, interpolation=cv2.INTER_AREA)

        # 对缩放后的帧进行超分辨率处理
        super_res_frame = self.model.upsample(scaled_frame)

        return cv2.resize(
                super_res_frame, original_size, interpolation=cv2.INTER_LINEAR
                )


class SuperResolutionLapSRNProcessor(SuperResolutionESPCNProcessor):
    def __init__(self, scale_factor=2):
        super().__init__()
        self.model.readModel(str(LapSRN_x2_FILE))
        self.scale_factor = scale_factor
        self.model.setModel("lapsrn", self.scale_factor)


# Example usage
if __name__ == "__main__":
    model_path = r"E:\load\python\Project\VideoFusion\bin\LapSRN_x2.pb"  # 需要提供你的ESPCN模型文件路径
    scale_factor = 2  # 根据你的模型设置的放大因子
    sr_processor = SuperResolutionESPCNProcessor()
    origin_img = cv2.imread(r"E:\load\python\Project\VideoFusion\TempAndTest\images\deband1 (2).jpg")
    print(origin_img)
    super_res_frame = sr_processor.process(origin_img)
    cv2.imshow("origin", origin_img)
    cv2.imshow("super_res_frame", super_res_frame)

    # cap = cv2.VideoCapture(r"E:\load\python\Project\VideoFusion\测试\video\black.mp4")
    # out = cv2.VideoWriter(r"E:\load\python\Project\VideoFusion\测试\video\black_out.mp4.mp4",
    #                       cv2.VideoWriter.fourcc(*'mp4v'), 30.0,
    #                       (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    #
    # # Get the total number of frames in the video
    # total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #
    # # Wrap the loop with tqdm for a progress bar
    # for _ in tqdm(range(total_frames), desc="Processing frames"):
    #     ret, frame = cap.read()
    #     if not ret:
    #         break
    #     super_res_frame = sr_processor.process(frame)
    #     out.write(super_res_frame)
    #
    # cap.release()
    # out.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()

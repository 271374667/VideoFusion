import cv2
import numpy as np

from src.common.processors.base_processor import OpenCVProcessor


class DeshakeProcessor(OpenCVProcessor):
    """
    https://github.com/lengkujiaai/video_stabilization
    """

    def __init__(self, max_corners=200, quality_level=0.01, min_distance=30, block_size=3, smoothing_radius=50):
        self.prev_pts = None
        self.prev_gray = None
        self.transforms = []
        self.max_corners = max_corners
        self.quality_level = quality_level
        self.min_distance = min_distance
        self.block_size = block_size
        self.smoothing_radius = smoothing_radius

    def process(self, frame: np.ndarray) -> np.ndarray:
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            return self._initialize_prev_frame_and_points(gray, frame)
        # Detect feature points in current frame
        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.prev_pts, None)

        # Filter only valid points
        idx = np.where(status == 1)[0]
        prev_pts = self.prev_pts[idx]
        curr_pts = curr_pts[idx]

        # Estimate the transformation matrix
        m, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)

        return frame if m is None else self._apply_transformation_and_fix_border(m, frame, gray)

    def _smooth_transforms(self):
        trajectory = np.cumsum(self.transforms, axis=0)
        smoothed_trajectory = self._smooth(trajectory)
        difference = smoothed_trajectory - trajectory
        self.transforms = self.transforms + difference

    def _smooth(self, trajectory):
        smoothed_trajectory = np.copy(trajectory)
        for i in range(3):
            smoothed_trajectory[:, i] = self._moving_average(trajectory[:, i], radius=self.smoothing_radius)
        return smoothed_trajectory

    def _moving_average(self, curve, radius):
        window_size = 2 * radius + 1
        f = np.ones(window_size) / window_size
        curve_pad = np.lib.pad(curve, (radius, radius), 'edge')
        curve_smoothed = np.convolve(curve_pad, f, mode='same')
        return curve_smoothed[radius:-radius]

    def fix_border(self, frame):
        s = frame.shape
        T = cv2.getRotationMatrix2D((s[1] / 2, s[0] / 2), 0, 1.04)
        frame = cv2.warpAffine(frame, T, (s[1], s[0]))
        return frame

    def _initialize_prev_frame_and_points(self, gray, arg1):
        # Initialize the previous frame and transforms array
        self.prev_gray = gray
        self.prev_pts = cv2.goodFeaturesToTrack(gray,
                                                maxCorners=self.max_corners,
                                                qualityLevel=self.quality_level,
                                                minDistance=self.min_distance,
                                                blockSize=self.block_size)
        return arg1

    def _apply_transformation_and_fix_border(self, m, frame, gray):
        # Extract translation and rotation
        dx = m[0, 2]
        dy = m[1, 2]
        da = np.arctan2(m[1, 0], m[0, 0])
        self.transforms.append([dx, dy, da])

        # Apply the transformation matrix to the current frame
        stabilized_frame = cv2.warpAffine(frame, m, (frame.shape[1], frame.shape[0]))
        stabilized_frame = self.fix_border(stabilized_frame)

        return self._initialize_prev_frame_and_points(gray, stabilized_frame)


if __name__ == '__main__':

    # Example usage
    deshake_processor = DeshakeProcessor()
    cap = cv2.VideoCapture(r"E:\load\python\Project\VideoFusion\测试\video\001.mp4")
    out = cv2.VideoWriter(r"E:\load\python\Project\VideoFusion\测试\video\001_out.mp4", cv2.VideoWriter.fourcc(*'mp4v'),
                          30.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        stabilized_frame = deshake_processor.process(frame)
        out.write(stabilized_frame)

    cap.release()
    out.release()

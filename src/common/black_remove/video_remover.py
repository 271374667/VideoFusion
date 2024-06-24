from pathlib import Path

import cv2
import loguru
import numpy as np

from src.signal_bus import SignalBus

signal_bus = SignalBus()


class VideoRemover:
    def start(self, video_path: Path | str) -> tuple[int, int, int, int]:
        video_path: Path = Path(video_path)
        loguru.logger.info(f'正在使用差值法检测视频变化区域: {video_path.name}')

        # 打开视频文件
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        signal_bus.set_detail_progress_max.emit(total_frames)
        ret, frame1 = cap.read()
        ret, frame2 = cap.read()

        # 初始化累计变化图像
        height, width = frame1.shape[:2]
        accumulated_changes = np.zeros((height, width), dtype=np.uint8)

        for frame_index in range(total_frames - 2):
            # 计算帧差异
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

            kernel = np.ones((5, 5), np.uint8)

            binary = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            # 找出图像中的连通区域
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)

            # 创建一个新的二值图像，用于保存去除孤立区域后的结果
            new_binary = np.zeros_like(binary)

            # 遍历所有连通区域
            for i in range(1, num_labels):
                # 如果该连通区域的大小大于阈值，则保留该区域
                if stats[i, cv2.CC_STAT_AREA] > 1500:  # 500是阈值，可以根据实际情况调整
                    new_binary[labels == i] = 255

            # 找到轮廓
            contours, _ = cv2.findContours(new_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 500:
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame1, (x, y), (x + w, y + h), (255, 255, 255), -1)
                cv2.rectangle(accumulated_changes, (x, y), (x + w, y + h), 255, -1)

            frame1 = frame2
            ret, frame2 = cap.read()
            signal_bus.set_detail_progress_current.emit(frame_index)

        cap.release()
        loguru.logger.debug(f'检测视频变化区域完成: {video_path.name}')

        # 找到累计变化图像中的轮廓以确定最大变化区域
        contours, _ = cv2.findContours(accumulated_changes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_rect = (0, 0, 0, 0)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area > max_area:
                max_area = area
                max_rect = (x, y, w, h)

        signal_bus.set_detail_progress_finish.emit()

        # 返回变化区域图像和最大矩形区域
        loguru.logger.debug(f'最大变化区域: x={max_rect[0]}, y={max_rect[1]}, w={max_rect[2]}, h={max_rect[3]}')

        return max_rect


if __name__ == '__main__':
    # 使用示例
    video_path = r"E:\load\python\Project\VideoFusion\TempAndTest\dy\b7bb97e21600b07f66c21e7932cb7550.mp4"
    video_remover = VideoRemover()
    max_rectangle = video_remover.start(video_path)

    print(f"Largest rectangle: x={max_rectangle[0]}, y={max_rectangle[1]}, w={max_rectangle[2]}, h={max_rectangle[3]}")

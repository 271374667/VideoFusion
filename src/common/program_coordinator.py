import os
from collections import Counter
from pathlib import Path

import loguru

from src.common.black_remove_algorithm.img_black_remover import IMGBlackRemover
from src.common.black_remove_algorithm.video_remover import VideoRemover
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.common.video_handler import VideoHandler
from src.common.video_info_reader import VideoInfoReader
from src.config import BlackBorderAlgorithm, cfg
from src.core.datacls import VideoInfo
from src.core.enums import Orientation, Rotation
from src.signal_bus import SignalBus
from src.utils import move_file_to_output_dir


class ProgramCoordinator:
    def __init__(self):
        self.is_running: bool = True
        self.is_merging: bool = False

        self._signal_bus = SignalBus()
        self._processor_global_var = ProcessorGlobalVar()
        self._video_handler = VideoHandler()

    def process(self, input_video_path_list: list[Path], orientation: Orientation, rotation: Rotation) -> Path:
        finished_video_path_list: list[Path] = []
        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_reset.emit()
        self._processor_global_var.clear()

        black_remove_algorithm_enum: BlackBorderAlgorithm = cfg.get(cfg.video_black_border_algorithm)
        match black_remove_algorithm_enum:
            case BlackBorderAlgorithm.DYNAMIC:
                black_remove_algorithm_impl = VideoRemover()
            case BlackBorderAlgorithm.STATIC:
                black_remove_algorithm_impl = IMGBlackRemover()
            case BlackBorderAlgorithm.DISABLE:
                black_remove_algorithm_impl = None
            case _:
                raise ValueError(f"不支持的黑边去除算法{black_remove_algorithm_enum}")

        self._processor_global_var.get_data()['orientation'] = orientation
        self._processor_global_var.get_data()['rotation_angle'] = rotation.value

        self._signal_bus.set_total_progress_max.emit(len(input_video_path_list))
        self._signal_bus.set_total_progress_description.emit("处理视频")

        video_info_list: list[VideoInfo] = []
        for each_path in input_video_path_list:
            if not self.is_running:
                break
            video_info = VideoInfoReader(str(each_path)).get_video_info(black_remove_algorithm_impl)
            video_info_list.append(video_info)

        best_width, best_height = self._get_best_resolution(video_info_list, orientation)
        self._processor_global_var.get_data()['target_width'] = best_width
        self._processor_global_var.get_data()['target_height'] = best_height

        for video_info in video_info_list:
            self._update_processor_global_var_with_crop_info(video_info)

            finished_video_path: Path = self._video_handler.process_video(video_info.video_path)
            finished_video_path_list.append(finished_video_path)
            self._signal_bus.advance_total_progress.emit(1)

        is_merge: bool = cfg.get(cfg.merge_video)
        if is_merge:
            finished_video_path = self._video_handler.merge_videos(finished_video_path_list)
            finished_video_path_list.clear()
            finished_video_path_list.append(finished_video_path)

        output_dir = move_file_to_output_dir(finished_video_path_list)
        os.startfile(output_dir)

        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        return output_dir

    def _update_processor_global_var_with_crop_info(self, video_info: VideoInfo):
        if video_info.crop:
            self._processor_global_var.get_data()['crop_x'] = video_info.crop.x
            self._processor_global_var.get_data()['crop_y'] = video_info.crop.y
            self._processor_global_var.get_data()['crop_width'] = video_info.crop.w
            self._processor_global_var.get_data()['crop_height'] = video_info.crop.h

    def _get_best_resolution(self, video_info_list: list[VideoInfo], video_orientation: Orientation) -> tuple[int, int]:
        def get_most_compatible_resolution(video_info_list: list[VideoInfo],
                                           orientation: Orientation) -> tuple[int, int]:
            """获取最合适的视频分辨率"""
            resolutions: list[tuple[int, int]] = []
            for each in video_info_list:
                width, height = (each.crop.w, each.crop.h) if each.crop else (each.width, each.height)

                # 判断视频的方向,如果视频的方向和用户选择的方向不一致则需要调换宽高
                if (orientation == Orientation.HORIZONTAL and width > height) or (
                        orientation == Orientation.VERTICAL and width < height):
                    resolutions.append((width, height))
                else:
                    resolutions.append((height, width))

            aspect_ratios: list[float] = [i[0] / i[1] for i in resolutions]
            most_common_ratio = Counter(aspect_ratios).most_common(1)[0][0]
            compatible_resolutions = [res for res in resolutions if (res[0] / res[1]) == most_common_ratio]
            compatible_resolutions.sort(key=lambda x: (x[0] * x[1]), reverse=True)
            width, height = compatible_resolutions[0][:2]
            return width, height

        loguru.logger.debug('正在获取最佳分辨率')
        self._signal_bus.set_total_progress_description.emit("调优参数")
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        best_width, best_height = get_most_compatible_resolution(video_info_list, video_orientation)
        loguru.logger.info(f'最佳分辨率获取完成,最佳分辨率为: {best_width}x{best_height}')
        return best_width, best_height


if __name__ == '__main__':
    p = ProgramCoordinator()
    print(p.process([
            Path(r"E:\load\python\Project\VideoFusion\测试\dy\8fd68ff8825a0de6aff59c482abe7147.mp4"),
            Path(r"E:\load\python\Project\VideoFusion\测试\dy\b7bb97e21600b07f66c21e7932cb7550.mp4")
            ],

            Orientation.HORIZONTAL,
            Rotation.CLOCKWISE))

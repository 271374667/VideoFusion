import os
import time
from collections import Counter
from pathlib import Path

import loguru

from src.common.black_remove_algorithm.img_black_remover import IMGBlackRemover
from src.common.black_remove_algorithm.video_remover import VideoRemover
from src.common.processors.processor_global_var import ProcessorGlobalVar
from src.common.task_resumer.task_resumer import TaskDict, TaskResumer
from src.common.task_resumer.task_resumer_manager import TaskResumerManager
from src.common.video_handler import VideoHandler
from src.common.video_info_reader import VideoInfoReader
from src.config import BlackBorderAlgorithm, VideoProcessEngine, cfg
from src.core.datacls import VideoInfo
from src.core.enums import FileProcessType, Orientation, Rotation
from src.signal_bus import SignalBus
from src.utils import move_file_to_output_dir


class ProgramCoordinator:
    def __init__(self):
        self._start_time = time.time()

        self._signal_bus = SignalBus()
        self._task_resumer_manager = TaskResumerManager()
        self._processor_global_var = ProcessorGlobalVar()
        self._video_handler = VideoHandler()

    def process(self, input_video_path_list: list[Path], orientation: Orientation, rotation: Rotation) -> Path | None:
        # sourcery skip: low-code-quality
        self._processor_global_var.clear()
        self._processor_global_var.update('orientation', orientation)
        self._processor_global_var.update('rotation_angle', rotation.value)
        loguru.logger.debug(self._processor_global_var)

        engine_type: VideoProcessEngine = cfg.get(cfg.video_process_engine)
        finished_video_path_list: list[Path] = []

        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_reset.emit()

        black_remove_algorithm_enum: BlackBorderAlgorithm = cfg.get(cfg.video_black_border_algorithm)
        match black_remove_algorithm_enum:
            case BlackBorderAlgorithm.Dynamic:
                black_remove_algorithm_impl = VideoRemover()
            case BlackBorderAlgorithm.Static:
                black_remove_algorithm_impl = IMGBlackRemover()
            case BlackBorderAlgorithm.Disable:
                black_remove_algorithm_impl = None
            case _:
                raise ValueError(f"不支持的黑边去除算法{black_remove_algorithm_enum}")

        self._signal_bus.set_total_progress_max.emit(len(input_video_path_list))
        self._signal_bus.set_total_progress_description.emit("分析视频")

        # 读取视频信息
        video_info_list: list[VideoInfo] = []
        for each_path in input_video_path_list:
            video_info = VideoInfoReader(str(each_path)).get_video_info(black_remove_algorithm_impl)
            loguru.logger.debug(video_info)
            video_info_list.append(video_info)

            self._signal_bus.advance_total_progress.emit(1)

        best_width, best_height = self._get_best_resolution(video_info_list, orientation)
        self._processor_global_var.get_data()['target_width'] = best_width
        self._processor_global_var.get_data()['target_height'] = best_height
        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()

        # 将每个任务添加到任务恢复器
        for video_info in video_info_list:
            task_resumer = TaskResumer(video_info.video_path)
            task_info: TaskDict = {
                    "input_video_path": str(video_info.video_path),
                    "task_status": 0,
                    "target_width": best_width,
                    "target_height": best_height,
                    "crop_x": video_info.crop.x if video_info.crop else None,
                    "crop_y": video_info.crop.y if video_info.crop else None,
                    "crop_width": video_info.crop.w if video_info.crop else None,
                    "crop_height": video_info.crop.h if video_info.crop else None,
                    }
            task_resumer.set_data_dict(task_info)
            self._task_resumer_manager.append_task(task_resumer)
            self._task_resumer_manager.save()
        loguru.logger.debug(f'任务恢复器保存完成,任务数:{len(self._task_resumer_manager.get_task_list())}')
        # 逐个处理视频
        self._signal_bus.set_total_progress_reset.emit()
        self._signal_bus.set_detail_progress_reset.emit()
        self._signal_bus.set_total_progress_description.emit("处理视频")
        self._signal_bus.set_total_progress_max.emit(len(video_info_list))
        for index, each_resumer in enumerate(self._task_resumer_manager.get_task_list()):
            video_info: VideoInfo = video_info_list[index]
            self._processor_global_var.get_data()['fps'] = video_info.fps
            self._processor_global_var.get_data()['total_frames'] = video_info.frame_count
            self._processor_global_var.get_data()['width'] = video_info.width
            self._processor_global_var.get_data()['height'] = video_info.height

            try:
                self._update_processor_global_var_with_crop_info(each_resumer.get_crop_x(),
                                                                 each_resumer.get_crop_y(),
                                                                 each_resumer.get_crop_width(),
                                                                 each_resumer.get_crop_height())

                finished_video_path: Path = self._video_handler.process_video(each_resumer.get_input_video_path())
                finished_video_path_list.append(finished_video_path)
                each_resumer.set_output_video_path(finished_video_path)  # 每一个已经处理完成的视频的路径,用来任务判断是否完成
                each_resumer.set_status_completed()
                loguru.logger.info(f'处理视频{each_resumer.get_input_video_path()}完成')
            except Exception as e:
                loguru.logger.error(f'处理视频{each_resumer.get_input_video_path()}失败,原因:{e}')
                self._current_total_task_status = FileProcessType.FAILED
            finally:
                self._signal_bus.advance_total_progress.emit(1)
                self._task_resumer_manager.save()

        is_merge: bool = cfg.get(cfg.merge_video)
        if is_merge:
            self.is_merging = True
            finished_video_path = self._video_handler.merge_videos(finished_video_path_list)
            finished_video_path_list.clear()
            finished_video_path_list.append(finished_video_path)
            self.is_merging = False

        output_dir = move_file_to_output_dir(finished_video_path_list)
        os.startfile(output_dir)

        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        self._signal_bus.finished.emit()
        loguru.logger.info(
                f'程序执行完成一共处理{len(input_video_path_list)}个视频,耗时: {time.time() - self._start_time}秒')
        if self._current_total_task_status != FileProcessType.FAILED:
            self._current_total_task_status = FileProcessType.COMPLETED
        self._task_resumer_manager.set_total_task_status(self._current_total_task_status)
        self._task_resumer_manager.save()
        return output_dir

    def _update_processor_global_var_with_crop_info(self, x: int | None = None,
                                                    y: int | None = None,
                                                    width: int | None = None,
                                                    height: int | None = None):
        self._processor_global_var.get_data()['crop_x'] = x
        self._processor_global_var.get_data()['crop_y'] = y
        self._processor_global_var.get_data()['crop_width'] = width
        self._processor_global_var.get_data()['crop_height'] = height

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
            Path(r"E:\load\python\Project\VideoFusion\TempAndTest\other\video_2024-03-04_16-55-20.mp4"),
            Path(r"E:\load\python\Project\VideoFusion\测试\dy\b7bb97e21600b07f66c21e7932cb7550.mp4")
            ],

            Orientation.HORIZONTAL,
            Rotation.CLOCKWISE))

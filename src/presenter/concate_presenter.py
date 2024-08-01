import random
import time
from pathlib import Path

import cv2
import loguru
import numpy as np
from PySide6.QtCore import QSize, QUrl, Qt
from PySide6.QtGui import QImage, QPixmap, QTransform
from PySide6.QtWidgets import QFileDialog

from src.common.black_remove.img_black_remover import BlackRemover
from src.common.task_resumer.task_resumer_manager import TaskResumer, TaskResumerManager
from src.config import PreviewFrame, VideoProcessEngine, cfg
from src.core.enums import Orientation, Rotation
from src.core.paths import FFMPEG_FILE
from src.model.concate_model import ConcateModel
from src.signal_bus import SignalBus
from src.utils import RunInThread, TempDir, trans_second_to_human_time
from src.view.concate_view import ConcateView


class ConcatePresenter:
    def __init__(self):
        self._signal_bus = SignalBus()
        self._black_remover = BlackRemover()
        self.current_rotation: int = 0
        self.start_time: float = time.time()
        self._temp_dir = TempDir()

        self._view: ConcateView = ConcateView()
        self._model: ConcateModel = ConcateModel()
        self._connect_signal()

    def get_view(self) -> ConcateView:
        return self._view

    def get_model(self) -> ConcateModel:
        return self._model

    def start(self):
        if self.get_view().get_horization_video_radio_btn().isChecked():
            video_orientation = Orientation.HORIZONTAL
        else:
            video_orientation = Orientation.VERTICAL

        rotation2cn: dict[Rotation, str] = {
                Rotation.CLOCKWISE: "顺时针旋转90°",
                Rotation.COUNTERCLOCKWISE: "逆时针旋转90°",
                Rotation.UPSIDE_DOWN: "上下颠倒",
                Rotation.NOTHING: "什么都不做"
                }

        cn2rotation: dict[str, Rotation] = {
                v: k for k, v in rotation2cn.items()
                }
        video_rotation = cn2rotation[self.get_view().get_rotate_video_cb().currentText()]
        video_engine: VideoProcessEngine = cfg.get(cfg.video_process_engine)
        self._task_resumer_manager = TaskResumerManager(video_engine, video_orientation, video_rotation)

        if not FFMPEG_FILE.exists():
            self.get_view().show_error_infobar("错误",
                                               "ffmpeg文件不存在无法进行视频合成,请检查bin目录下是否有ffmpeg.exe文件",
                                               is_closable=True)
            return

        # 读取本地文件并获取任务列表
        if self._task_resumer_manager.is_json_exist():
            last_completed = bool(self._task_resumer_manager.check_last_task_completed())
            uncompleted_task_list: list[TaskResumer] = self._task_resumer_manager.get_uncompleted_task_list()
        else:
            last_completed = False
            uncompleted_task_list = []

        if (
                not last_completed
                and uncompleted_task_list
                and self.get_view().show_mask_dialog(
                "恢复上一次的任务", "您的上一次任务还未完成,是否继续上一次的任务?"
                )
        ):
            video_list = [x.get_input_video_path() for x in uncompleted_task_list]
            self.get_view().show_info_infobar("提示", "上一次的任务已经完成,开始新的任务", 3000)
        else:
            video_list = self.get_all_video_files()

        if not video_list:
            loguru.logger.warning("请先选择视频文件")
            self.get_view().show_warning_infobar("错误", "您还没有添加任何视频文件")
            return

        self._signal_bus.started.emit()
        self._set_btns_enable(False, True)
        self.get_model().start(video_list, video_orientation, video_rotation)
        self.start_time = time.time()
        self.get_view().show_state_tooltip("运行中……", "请耐心等待,程序正在运行")

    def finished(self):
        self._set_btns_enable(True, False)
        used_time: int = int(time.time() - self.start_time)
        self.get_view().show_info_infobar("完成", f"视频合并完成,总共耗时{trans_second_to_human_time(used_time)}",
                                          duration=10000, is_closable=True)
        output_path = cfg.get(cfg.output_dir)
        self.get_view().finish_state_tooltip("完成", f"视频合并完成,输出文件至: {output_path}")

    def cancle_worker(self):
        if self.get_model().is_merging:
            self.get_view().show_warning_infobar("警告", "合并操作正在进行中,合并过程中无法取消任务,请等待合并完成")
            return

        self.get_model().set_running(False)

        self._set_btns_enable(True, False)
        self.get_view().finish_state_tooltip("取消", "合并操作已取消")
        self._signal_bus.set_total_progress_finish.emit()
        self._signal_bus.set_detail_progress_finish.emit()
        self._signal_bus.set_total_progress_description.emit("处理完成")
        self._signal_bus.finished.emit()

    def _set_btns_enable(self, start_btn_enable, cancle_btn_enable):
        self.get_view().get_start_btn().setEnabled(start_btn_enable)
        self.get_view().get_start_btn().setVisible(start_btn_enable)
        self.get_view().get_cancle_btn().setVisible(cancle_btn_enable)
        self.get_view().get_video_file_list_simple_card_widget().setEnabled(start_btn_enable)

    def get_all_video_files(self) -> list[str]:
        return self.get_view().get_video_file_list().get_draggable_list_view().get_all_items()

    def _select_video_files(self):
        # 能够多选视频文件
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        available_suffix: list[str] = ['.mp4', '.avi', '.mov', '.flv', '.mkv', '.rmvb', '.wmv', '.webm', '.ts', '.m4v']
        file_dialog.setNameFilters([f"Video Files (*{suffix})" for suffix in available_suffix])
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        target_dir = self._temp_dir.get_temp_dir()
        if current_item := self.get_view().get_video_file_list().get_current_item_text():
            target_dir = Path(current_item).parent
        file_dialog.setDirectory(str(target_dir))

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self.get_view().get_video_file_list().add_items(file_paths)
            loguru.logger.debug(f"本次一共选择了{len(file_paths)}个文件: {file_paths}")

    def _on_video_clicked(self):
        current_item: str = self.get_view().get_video_file_list().get_current_item_text()
        if not current_item or not Path(current_item).is_file():
            return

        # 设置预览图片
        preview_frame: PreviewFrame = cfg.get(cfg.preview_frame)
        if preview_frame == PreviewFrame.FirstFrame:
            self._show_first_frame()
        elif preview_frame == PreviewFrame.LastFrame:
            self._show_last_frame()
        elif preview_frame == PreviewFrame.RandomFrame:
            self._show_random_frame()

        # 设置视频播放器的视频
        try:
            video_widget = self.get_view().get_video_player()
            preview_auto_play: bool = cfg.get(cfg.preview_auto_play)
            video_widget.setVideo(QUrl.fromLocalFile(current_item))
            if preview_auto_play:
                video_widget.play()
            loguru.logger.debug(f"设置视频播放器的视频: {current_item}")
        except Exception as e:
            loguru.logger.error(f"设置视频播放器的视频失败: {e}")

    def _on_video_drop(self):
        # 获取列表中的第一个视频文件
        video_list = self.get_view().get_video_file_list().get_draggable_list_view()
        first_video_path: str = video_list.get_all_items()[0]
        if not video_list.count():
            self.get_view().show_warning_infobar("错误", "您还没有添加任何视频文件")
            return

        cap = cv2.VideoCapture(first_video_path)
        # 显示视频中不为黑色的第一帧(为了加快速度,只显示前50帧)
        for _ in range(50):
            ret, frame = cap.read()
            if not ret:
                break
            if not self._black_remover.is_black(frame):
                break
        self._show_frame_on_label(cap, '显示第一帧: ', first_video_path)

    # 图片预览
    def _show_first_frame(self):
        def frame_selector(cap):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self._show_frame(frame_selector)

    def _show_last_frame(self):
        def frame_selector(cap):
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)

        self._show_frame(frame_selector)

    def _show_random_frame(self):
        def frame_selector(cap):
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, random.randint(0, total_frames - 1))

        self._show_frame(frame_selector)

    def _show_frame(self, frame_selector):
        if not (current_item := self.get_view().get_video_file_list().currentItem()):
            return
        video_path = current_item.text()
        self.get_view().get_video_file_list().setEnabled(False)

        def start():
            cap = cv2.VideoCapture(video_path)
            frame_selector(cap)
            return cap

        def finished(cap):
            self._show_frame_on_label(cap, '显示帧: ', video_path)
            self.get_view().get_video_file_list().setEnabled(True)

        self._run_in_thread = RunInThread()
        self._run_in_thread.set_start_func(start)
        self._run_in_thread.set_finished_func(finished)
        self._run_in_thread.start()

    def _rotate_clockwise(self):
        # 先检查是否有图片
        img_lb = self.get_view().get_preview_pic_lb()
        if img_lb.pixmap():
            self.current_rotation = (self.current_rotation + 90) % 360
            self._rotate_img(90, '顺时针旋转图片, 当前角度: ')

    def _rotate_counterclockwise(self):
        # 先检查是否有图片
        img_lb = self.get_view().get_preview_pic_lb()
        if img_lb.pixmap():
            self.current_rotation = (self.current_rotation - 90) % 360
            self._rotate_img(-90, '逆时针旋转图片, 当前角度: ')

    def _rotate_upsidedown(self):
        # 先检查是否有图片
        img_lb = self.get_view().get_preview_pic_lb()
        if img_lb.pixmap():
            self.current_rotation = (self.current_rotation + 180) % 360
            self._rotate_img(180, '上下翻转图片, 当前角度: ')

    def _show_frame_on_label(self, cap, info_title: str, video_path: str):
        ret, frame = cap.read()
        if frame is None:
            self.get_view().show_error_infobar("错误",
                                               f"当前视频无法播放,请检查视频文件是否损坏或者尝试重新转码为H264格式视频\n{video_path}",
                                               duration=6000,
                                               is_closable=True)
            loguru.logger.error(f'当前视频无法播放,请检查视频文件是否损坏或者尝试重新转码为H264格式视频\n{video_path}')
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cap.release()
        if ret:
            self._set_img(frame)
            loguru.logger.debug(f"{info_title}{video_path}")

    def _rotate_img(self, angle: int, log_title: str):
        img_lb = self.get_view().get_preview_pic_lb()
        pixmap = img_lb.pixmap()
        pixmap = pixmap.transformed(QTransform().rotate(angle))
        # 缩放到标签大小
        img_lb = self.get_view().get_preview_pic_lb()
        pixmap = pixmap.scaled(img_lb.width(), img_lb.height(), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        img_lb.setPixmap(pixmap)
        loguru.logger.debug(f"{log_title}{self.current_rotation}")

    def _set_img(self, frame: np.ndarray):
        # 是否启用去除黑边
        img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        # 剪裁图片
        preview_video_remove_black: bool = cfg.get(cfg.preview_video_remove_black)
        if preview_video_remove_black:
            left_top_x, left_top_y, right_bottom_x, right_bottom_y = self._black_remover.start(img_array=frame)
            img = img.copy(left_top_x, left_top_y, right_bottom_x - left_top_x, right_bottom_y - left_top_y)

        # 旋转图片
        img = img.transformed(QTransform().rotate(self.current_rotation))

        # 将图片缩放到QLabel的大小
        img_lb = self.get_view().get_preview_pic_lb()
        img = img.scaled(img_lb.width(), img_lb.height(), Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)
        img_lb.setPixmap(QPixmap.fromImage(img))

    def _show_failed_infobar(self):
        self.get_view().show_error_infobar("错误",
                                           "当前视频合成出错,请前往控制台查看错误原因,您可以前往github提出issue或者检查视频是否出现损坏",
                                           is_closable=True)

    def resizeEvent(self, event):
        if img_lb := self.get_view().get_preview_pic_lb():
            img_lb.setMaximumSize(QSize(self.get_view().width() // 2, self.get_view().height() // 2))
            pixmap = img_lb.pixmap()
            pixmap = pixmap.scaled(img_lb.width(), img_lb.height(), Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            img_lb.setPixmap(pixmap)
        event.accept()

    def _connect_signal(self):
        self.get_view().get_select_video_btn().clicked.connect(self._select_video_files)
        self.get_view().get_video_file_list().get_draggable_list_view().itemClicked.connect(self._on_video_clicked)
        self.get_view().get_clockwise_rotate_btn().clicked.connect(self._rotate_clockwise)
        self.get_view().get_counterclockwise_rotate_btn().clicked.connect(self._rotate_counterclockwise)
        self.get_view().get_upside_down_rotate_btn().clicked.connect(self._rotate_upsidedown)
        self.get_view().get_start_btn().clicked.connect(self.start)
        self.get_view().get_cancle_btn().clicked.connect(self.cancle_worker)
        self._signal_bus.file_droped.connect(lambda x: self._on_video_drop())
        self._signal_bus.finished.connect(self.finished)
        self._signal_bus.failed.connect(self._show_failed_infobar)
        self.get_view().get_video_file_list().remove_action.triggered.connect(
                lambda: self._on_video_clicked())


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    presenter = ConcatePresenter()
    presenter.get_view().show()
    app.exec()

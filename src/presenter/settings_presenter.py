import loguru
from PySide6.QtWidgets import QFileDialog

from src.components.message_dialog import MessageDialog
from src.config import BlackBorderAlgorithm, SuperResolutionAlgorithm, VideoProcessEngine, cfg
from src.core.version import __version__
from src.model.settings_model import SettingsModel
from src.utils import RunInThread
from src.utils import VersionRequest
from src.view.settings_view import SettingView


class SettingsPresenter:
    def __init__(self):
        self._is_first_time: bool = True

        self._view: SettingView = SettingView()
        self._model: SettingsModel = SettingsModel()
        self._version_request = VersionRequest()
        self._message_dialog = MessageDialog()
        self._engine_changed()
        self._on_black_remove_changed()
        self._connect_signal()

    def get_view(self) -> SettingView:
        return self._view

    def get_model(self) -> SettingsModel:
        return self._model

    def _select_ffmpeg_file(self):
        # 选择ffmepg.exe的路径
        file_path, _ = QFileDialog.getOpenFileName(self._view, "选择FFmpeg.exe", "", "ffmpeg.exe (*.exe)")
        if file_path:
            cfg.set(cfg.ffmpeg_file, file_path)
            loguru.logger.info(f"选择了FFmpeg路径: {file_path}")
            self._view.ffmpeg_file_card.setToolTip(file_path)
            self.get_view().show_success_infobar("提示", "FFmpeg路径已经设置成功", duration=1000, is_closable=True)
            return
        self.get_view().show_error_infobar("错误", "请选择一个有效的FFmpeg路径", duration=3000, is_closable=True)

    def _select_temp_dir(self):
        if dir_path := QFileDialog.getExistingDirectory(
                self._view, "选择临时目录", ""
                ):
            cfg.set(cfg.temp_dir, dir_path)
            loguru.logger.info(f"选择了临时目录: {dir_path}")
            self._view.temp_dir_card.setToolTip(dir_path)
            self.get_view().show_success_infobar("提示", "临时目录已经设置成功", duration=1000, is_closable=True)
            return
        self.get_view().show_error_infobar("错误", "请选择一个有效的临时目录", duration=3000, is_closable=True)

    def _select_output_file_path(self):
        # 选择输出文件保存的位置
        output_file_path = QFileDialog.getSaveFileName(self._view, "选择输出文件路径", "输出文件.mp4",
                                                       "视频文件 (*.mp4)")
        if output_file_path[0]:
            cfg.set(cfg.output_dir, output_file_path[0])
            loguru.logger.info(f"选择了输出文件路径: {output_file_path[0]}")
            self._view.output_dir_path_card.setToolTip(output_file_path[0])
            self.get_view().show_success_infobar("提示", "输出文件路径已经设置成功", duration=1000, is_closable=True)
            return
        self.get_view().show_error_infobar("错误", "请选择一个有效的输出文件路径", duration=3000, is_closable=True)

    def _on_black_remove_changed(self):
        """动态去黑边算法和获取视频采样帧数不能同时启用"""
        black_remove_algorithm: BlackBorderAlgorithm = cfg.get(cfg.video_black_border_algorithm)
        if black_remove_algorithm == BlackBorderAlgorithm.DYNAMIC:
            self.get_view().video_sample_rate_card.setEnabled(False)
            return
        self.get_view().video_sample_rate_card.setEnabled(True)

    def _check_update(self):
        current_version = __version__

        def start():
            return self._version_request.get_latest_version()

        def finished(x):
            print(f'{x=}')
            latest_version, description = x
            if latest_version is None:
                self.get_view().show_error_infobar("错误",
                                                   "无法获取最新版本信息,请检查网络,或者自行前往官网下载最新版本",
                                                   duration=3000, is_closable=True)
                loguru.logger.error("无法获取最新版本信息")
                return

            latest_version = latest_version.replace("v", "")
            if latest_version > current_version:
                self._message_dialog.set_title("发现新版本")
                self._message_dialog.set_explain(f"发现新版本: {latest_version}, 当前版本: {current_version}")
                self._message_dialog.set_body(description)
                self._message_dialog.show()
                loguru.logger.info(f"发现新版本: {latest_version}, 当前版本: {current_version}")
                loguru.logger.info(f"更新内容: {description}")
                return

            self.get_view().show_info_infobar("提示", "当前已经是最新版本", duration=3000, is_closable=True)
            loguru.logger.info(f"当前已经是最新版本: {current_version}")

        self._run_in_thread = RunInThread()
        self._run_in_thread.set_start_func(start)
        self._run_in_thread.set_finished_func(finished)
        self._run_in_thread.start()

    def _engine_changed(self):
        current_engine: VideoProcessEngine = cfg.get(cfg.video_process_engine)

        if current_engine == VideoProcessEngine.OpenCV:
            self._update_engine_settings("当前使用OpenCV进行视频处理", True)
            return

        elif current_engine == VideoProcessEngine.FFmpeg:
            self._update_engine_settings("当前使用FFmpeg进行视频处理", False)
            self.get_view().white_balance_card.setValue(False)
            self.get_view().brightness_contrast_card.setValue(False)
            self.get_view().super_resolution_algorithm_card.setValue(SuperResolutionAlgorithm.DISABLE)
            return

    def _update_engine_settings(self, flag1, flag2):
        self._view.engine_card.setToolTip(flag1)
        if not self._is_first_time:
            self.get_view().show_success_infobar(
                    "提示", flag1, duration=1000, is_closable=True
                    )
        self._is_first_time = False
        self.get_view().white_balance_card.setEnabled(flag2)
        self.get_view().brightness_contrast_card.setEnabled(flag2)
        self.get_view().super_resolution_algorithm_card.setEnabled(flag2)

    def _connect_signal(self):
        self._view.ffmpeg_file_card.clicked.connect(self._select_ffmpeg_file)
        self._view.temp_dir_card.clicked.connect(self._select_temp_dir)
        self._view.output_dir_path_card.clicked.connect(self._select_output_file_path)
        self._view.update_card.clicked.connect(self._check_update)
        self._message_dialog.ok_btn.clicked.connect(self._message_dialog.close)
        self._message_dialog.cancel_btn.clicked.connect(self._message_dialog.close)
        self.get_view().engine_card.comboBox.currentIndexChanged.connect(self._engine_changed)
        self.get_view().video_black_border_algorithm_card.comboBox.currentIndexChanged.connect(
                self._on_black_remove_changed)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    settings_presenter = SettingsPresenter()
    settings_presenter.get_view().show()
    app.exec()

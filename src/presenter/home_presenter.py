import fnmatch
from pathlib import Path

import loguru

from src.components.sort_tool_component import QFileDialog, SortToolComponent
from src.core.enums import Orientation, Rotation
from src.model.home_model import HomeModel
from src.signal_bus import SignalBus
from src.view.home_view import HomeView


class HomePresenter:
    def __init__(self):
        self._view: HomeView = HomeView()
        self._model: HomeModel = HomeModel()
        self._sort_tool_component: SortToolComponent = SortToolComponent()
        self._signal_bus: SignalBus = SignalBus()

        self.get_view().get_enter_tool_btn().clicked.connect(self._enter_tool)
        self.get_view().get_open_browser_btn().clicked.connect(self._open_dir_or_txt_file)
        self.get_view().get_output_btn().clicked.connect(self._set_output_save_file_path)
        self.get_view().get_start_btn().clicked.connect(self._start)

        # 绑定进度条
        self._signal_bus.set_total_progress_current.connect(self._set_total_progress_value)
        self._signal_bus.set_total_progress_max.connect(self._set_total_progress_maximum)
        self._signal_bus.advance_total_progress.connect(self._advance_total_progress)
        self._signal_bus.set_total_progress_description.connect(self._set_total_progress_description)
        self._signal_bus.set_total_progress_finish.connect(self._finish_total_progress)
        self._signal_bus.set_total_progress_reset.connect(self._reset_total_progress)
        self._signal_bus.set_detail_progress_current.connect(self._set_detail_progress_value)
        self._signal_bus.set_detail_progress_max.connect(self._set_detail_progress_maximum)
        self._signal_bus.advance_detail_progress.connect(self._advance_detail_progress)
        self._signal_bus.set_detail_progress_description.connect(self._set_detail_progress_description)
        self._signal_bus.set_detail_progress_finish.connect(self._finish_detail_progress)
        self._signal_bus.set_detail_progress_reset.connect(self._reset_detail_progress)

        self._signal_bus.file_droped.connect(self._drop_file_or_dir)

        self._signal_bus.finished.connect(self._run_finished)

    def get_view(self) -> HomeView:
        return self._view

    def get_model(self) -> HomeModel:
        return self._model

    def _open_dir_or_txt_file(self):
        is_die_mode: bool = self.get_view().get_dir_rb().isChecked()
        if is_die_mode:
            path = QFileDialog.getExistingDirectory(self.get_view(), "选择文件夹")
            # 将路径设置到输入框中
            self.get_view().get_input_le().setText(path)

            # 同时将输出文件夹设置为输入文件夹
            path = Path(path)
            path / "output.mp4"
            self.get_view().get_output_le().setText(str(path))
        else:
            path, _ = QFileDialog.getOpenFileName(self.get_view(), "选择文件", "", "Text Files (*.txt)")
            # 将路径设置到输入框中
            self.get_view().get_input_le().setText(path)
            path = Path(path)
            path = path.parent / "output.mp4"

    def _drop_file_or_dir(self, path: str):
        is_die_mode: bool = self.get_view().get_dir_rb().isChecked()
        if is_die_mode:
            # 将路径设置到输入框中
            self.get_view().get_input_le().setText(path)

            # 同时将输出文件夹设置为输入文件夹
            path = Path(path)
            path / "output.mp4"
            self.get_view().get_output_le().setText(str(path))
        else:
            # 将路径设置到输入框中
            self.get_view().get_input_le().setText(path)
            path = Path(path)
            path = path.parent / "output.mp4"
            self.get_view().get_output_le().setText(str(path))

    def _set_output_save_file_path(self):
        path, _ = QFileDialog.getSaveFileName(self.get_view(), "选择文件", "", "Text Files (*.mp4)")
        if path:
            self.get_view().get_output_le().setText(path)

    def _set_total_progress_value(self, value: int):
        self.get_view().set_total_progress_value(value)

    def _set_total_progress_maximum(self, value: int):
        self.get_view().set_total_progress_max(value)

    def _advance_total_progress(self, value: int):
        self.get_view().advance_total_progress(value)

    def _set_total_progress_description(self, description: str):
        self.get_view().set_total_progress_description(description)

    def _finish_total_progress(self):
        self.get_view().finish_total_progress()

    def _reset_total_progress(self):
        self.get_view().reset_total_progress()

    def _set_detail_progress_value(self, value: int):
        self.get_view().set_detail_progress_value(value)

    def _set_detail_progress_maximum(self, value: int):
        self.get_view().set_detail_progress_max(value)

    def _advance_detail_progress(self, value: int):
        self.get_view().advance_detail_progress(value)

    def _set_detail_progress_description(self, description: str):
        self.get_view().set_detail_progress_description(description)

    def _finish_detail_progress(self):
        self.get_view().finish_detail_progress()

    def _reset_detail_progress(self):
        self.get_view().reset_detail_progress()

    def _run_finished(self):
        self.get_view().get_start_btn().setEnabled(True)
        self.get_view().show_info_message("处理完成！")

    def _enter_tool(self):
        self._sort_tool_component.show()

    def _start(self):
        orientation2cn: dict[Orientation, str] = {
                Orientation.HORIZONTAL: "横屏视频",
                Orientation.VERTICAL: "竖屏视频"
                }

        rotation2cn: dict[Rotation, str] = {
                Rotation.CLOCKWISE: "顺时针旋转90°",
                Rotation.COUNTERCLOCKWISE: "逆时针旋转90°",
                Rotation.UPSIDE_DOWN: "上下颠倒",
                Rotation.NOTHING: "什么都不做"
                }

        cn2orientation: dict[str, Orientation] = {
                v: k for k, v in orientation2cn.items()
                }

        cn2rotation: dict[str, Rotation] = {
                v: k for k, v in rotation2cn.items()
                }

        self.get_view().get_start_btn().setEnabled(False)
        is_dir: bool = self.get_view().get_dir_rb().isChecked()
        dir_or_file: str = self.get_view().get_input_le().text()
        output_file: str = self.get_view().get_output_le().text()
        dir_mode: str = self.get_view().get_dir_mode_le().text()
        fps: int = self.get_view().get_fps_spin().value()
        sample_rate: float = self.get_view().get_sample_rate_spin().value()
        video_orientation: str = self.get_view().get_video_oritation_cb().currentText()
        video_orientation: Orientation = cn2orientation[video_orientation]
        horizontal_rotation: str = self.get_view().get_horization_rotation_cb().currentText()
        horizontal_rotation: Rotation = cn2rotation[horizontal_rotation]
        vertical_rotation: str = self.get_view().get_vertical_rotation_cb().currentText()
        vertical_rotation: Rotation = cn2rotation[vertical_rotation]

        if not dir_or_file:
            self.get_view().show_error_message("请选择文件或文件夹")
            loguru.logger.error("错误: 未选择文件或文件夹")
            return

        if not output_file:
            self.get_view().show_error_message("请选择输出文件")
            loguru.logger.error("错误: 未选择输出文件")
            return

        if self.get_view().get_dir_mode_le().text() != "":
            # 判断输出是否符合fnmatch规则
            try:
                fnmatch.translate(dir_mode)
            except Exception as e:
                self.get_view().show_error_message(f"输出文件夹匹配规则有误:{e}")
                loguru.logger.error(f"错误: 输出文件夹匹配规则有误:{e}")
                return
            return
        else:
            dir_mode = self.get_view().get_dir_mode_le().placeholderText()

        self.get_model().start(is_dir, dir_or_file, output_file, dir_mode, fps, sample_rate, video_orientation,
                               horizontal_rotation, vertical_rotation)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    h = HomePresenter()
    h.get_view().show()
    app.exec()

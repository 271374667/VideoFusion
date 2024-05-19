from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QComboBox, QCommandLinkButton, QDoubleSpinBox, QLabel, QLineEdit, QMenu,
                               QMessageBox, QProgressBar, QPushButton, QRadioButton, QSpinBox, QTextEdit, QWidget)

from src.about import about_txt
from src.core.enums import Orientation, Rotation
from src.interface.Ui_home_page import Ui_Form


class HomeView(QWidget):
    def __init__(self):
        super().__init__()

        self._current_total_progress_value: int = 0
        self._current_total_progress_max: int = 0
        self._current_detail_progress_description: str = ""
        self._current_detail_progress_value: int = 0
        self._current_detail_progress_max: int = 0
        self._current_detail_progress_description: str = ""

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self._about_textedit = QTextEdit()
        self._about_textedit.setText(about_txt)
        self._about_textedit.setReadOnly(True)
        self._about_textedit.resize(600, 400)
        self._about_textedit.setWindowTitle("关于本软件")

        self._orientation2cn: dict[Orientation, str] = {
                Orientation.HORIZONTAL: "横屏视频",
                Orientation.VERTICAL: "竖屏视频"
                }

        self._rotation2cn: dict[Rotation, str] = {
                Rotation.CLOCKWISE: "顺时针旋转90°",
                Rotation.COUNTERCLOCKWISE: "逆时针旋转90°",
                Rotation.UPSIDE_DOWN: "上下颠倒",
                Rotation.NOTHING: "什么都不做"
                }

        self._cn2orientation: dict[str, Orientation] = {
                v: k for k, v in self._orientation2cn.items()
                }

        self._cn2rotation: dict[str, Rotation] = {
                v: k for k, v in self._rotation2cn.items()
                }

        for e in Orientation:
            self.get_video_oritation_cb().addItem(self._orientation2cn[e])
        for e in Rotation:
            self.get_vertical_rotation_cb().addItem(self._rotation2cn[e])
            self.get_horization_rotation_cb().addItem(self._rotation2cn[e])

        self.get_video_oritation_cb().currentTextChanged.connect(self._video_oritation_changed)

        self.get_video_oritation_cb().setCurrentIndex(0)
        self.get_horization_rotation_cb().setCurrentIndex(0)
        self.get_vertical_rotation_cb().setCurrentIndex(0)

    def get_input_le(self) -> QLineEdit:
        return self.ui.lineEdit

    def get_txt_rb(self) -> QRadioButton:
        return self.ui.radioButton_2

    def get_dir_rb(self) -> QRadioButton:
        return self.ui.radioButton

    def get_open_browser_btn(self) -> QPushButton:
        return self.ui.pushButton_2

    def get_dir_mode_le(self) -> QLineEdit:
        return self.ui.lineEdit_2

    def get_output_le(self) -> QLineEdit:
        return self.ui.lineEdit_3

    def get_output_btn(self) -> QPushButton:
        return self.ui.pushButton_3

    def get_fps_spin(self) -> QSpinBox:
        return self.ui.spinBox

    def get_sample_rate_spin(self) -> QDoubleSpinBox:
        return self.ui.doubleSpinBox

    def get_video_oritation_cb(self) -> QComboBox:
        return self.ui.comboBox

    def get_horization_rotation_cb(self) -> QComboBox:
        return self.ui.comboBox_2

    def get_horization_rotation_lb(self) -> QLabel:
        return self.ui.label_9

    def get_vertical_rotation_cb(self) -> QComboBox:
        return self.ui.comboBox_3

    def get_vertical_rotation_lb(self) -> QLabel:
        return self.ui.label_10

    def get_total_progress_bar(self) -> QProgressBar:
        return self.ui.progressBar

    def get_total_progress_lb(self) -> QLabel:
        return self.ui.label

    def get_detail_progress_bar(self) -> QProgressBar:
        return self.ui.progressBar_2

    def get_detail_progress_lb(self) -> QLabel:
        return self.ui.label_2

    def get_start_btn(self) -> QPushButton:
        return self.ui.pushButton

    def get_enter_tool_btn(self) -> QCommandLinkButton:
        return self.ui.commandLinkButton

    def set_total_progress_value(self, value: int):
        self.get_total_progress_bar().setValue(value)
        self._current_total_progress_value = value
        self.get_total_progress_bar().update()

    def set_total_progress_max(self, value: int):
        self.get_total_progress_bar().setMaximum(value)
        self._current_total_progress_max = value
        self.get_total_progress_bar().update()

    def advance_total_progress(self, value: int):
        self._current_total_progress_value = self._current_total_progress_value + value
        self.get_total_progress_bar().setValue(self._current_total_progress_value)
        self.get_total_progress_bar().update()

    def set_total_progress_description(self, description: str):
        self._current_detail_progress_description = description
        self.get_total_progress_lb().setText(description)
        self.get_total_progress_bar().update()

    def finish_total_progress(self):
        self.get_total_progress_bar().setValue(self._current_total_progress_max)
        self.get_total_progress_bar().update()

    def reset_total_progress(self):
        self.set_total_progress_max(0)
        self.set_total_progress_value(0)
        self.get_total_progress_bar().update()

    def set_detail_progress_value(self, value: int):
        self.get_detail_progress_bar().setValue(value)
        self._current_detail_progress_value = value
        self.get_detail_progress_bar().update()

    def set_detail_progress_max(self, value: int):
        self.get_detail_progress_bar().setMaximum(value)
        self._current_detail_progress_max = value
        self.get_detail_progress_bar().update()

    def advance_detail_progress(self, value: int):
        self._current_detail_progress_value = self._current_detail_progress_value + value
        self.get_detail_progress_bar().setValue(self._current_detail_progress_value)
        self.get_detail_progress_bar().update()

    def set_detail_progress_description(self, description: str):
        self._current_detail_progress_description = description
        self.get_detail_progress_lb().setText(description)
        self.get_detail_progress_bar().update()

    def finish_detail_progress(self):
        self.get_detail_progress_bar().setValue(self._current_detail_progress_max)
        self.get_detail_progress_bar().update()

    def reset_detail_progress(self):
        self.set_detail_progress_max(0)
        self.set_detail_progress_value(0)
        self.get_detail_progress_bar().update()

    def show_error_message(self, message: str):
        error_message = QMessageBox(self)
        # 设置图标
        error_message.setIcon(QMessageBox.Icon.Critical)
        error_message.setText(message)
        error_message.setWindowTitle("错误")
        error_message.resize(300, 200)
        error_message.exec()

    def show_info_message(self, message: str):
        info_message = QMessageBox(self)
        info_message.setIcon(QMessageBox.Icon.Information)
        info_message.setText(message)
        info_message.setWindowTitle("提示")
        info_message.resize(300, 200)
        info_message.exec()

    def _video_oritation_changed(self, changed_text: str):
        if changed_text == self._orientation2cn[Orientation.VERTICAL]:
            self.get_vertical_rotation_cb().setEnabled(False)
            self.get_vertical_rotation_lb().setEnabled(False)
            self.get_horization_rotation_cb().setEnabled(True)
            self.get_horization_rotation_lb().setEnabled(True)
        elif changed_text == self._orientation2cn[Orientation.HORIZONTAL]:
            self.get_vertical_rotation_cb().setEnabled(True)
            self.get_vertical_rotation_lb().setEnabled(True)
            self.get_horization_rotation_cb().setEnabled(False)
            self.get_horization_rotation_lb().setEnabled(False)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        new_act = QAction('关于本软件', self)
        context_menu.addAction(new_act)
        new_act.triggered.connect(self._about_textedit.show)
        context_menu.exec(event.globalPos())


if __name__ == '__main__':
    app = QApplication([])
    h = HomeView()
    h.show()
    app.exec()

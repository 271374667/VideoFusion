import re

from PySide6.QtWidgets import QApplication, QLabel, QStackedWidget, QWidget
from qfluentwidgets.components import (BodyLabel, ComboBox, PrimaryPushButton, ProgressBar, PushButton,
                                       RadioButton, SegmentedWidget)
from qfluentwidgets.multimedia import VideoWidget

from src.components.draggable_list_widget import DraggableListWidget
from src.core.enums import Rotation
from src.interface.Ui_concate_page import Ui_Form
from src.signal_bus import SignalBus
from src.view.message_base_view import MessageBaseView

WINDOW_RENAME_FILE_REGEX = re.compile(r'.*?\((\d+)\)\..*?')
TIME_FILE_REGEX = re.compile(r'.*?([1-2]\d{3}).([0-1]\d).([0-3]\d).*?')


class ConcateView(MessageBaseView):
    def __init__(self):
        super().__init__()
        self.setObjectName("ConcateView")
        self._signal_bus = SignalBus()

        self._current_total_progress_value: int = 0
        self._current_total_progress_max: int = 0
        self._current_detail_progress_description: str = ""
        self._current_detail_progress_value: int = 0
        self._current_detail_progress_max: int = 0
        self._current_detail_progress_description: str = ""

        self._rotation2cn: dict[Rotation, str] = {
                Rotation.CLOCKWISE: "顺时针旋转90°",
                Rotation.COUNTERCLOCKWISE: "逆时针旋转90°",
                Rotation.UPSIDE_DOWN: "上下颠倒",
                Rotation.NOTHING: "什么都不做"
                }

        self._cn2rotation: dict[str, Rotation] = {
                v: k for k, v in self._rotation2cn.items()
                }

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self._initialize()

        # 之后可能presenter写的有点多,这里把进度条直接和界面绑定
        self._signal_bus.set_total_progress_current.connect(self.set_total_progress_value)
        self._signal_bus.set_total_progress_max.connect(self.set_total_progress_max)
        self._signal_bus.advance_total_progress.connect(self.advance_total_progress)
        self._signal_bus.set_total_progress_description.connect(self.set_total_progress_description)
        self._signal_bus.set_total_progress_finish.connect(self.finish_total_progress)
        self._signal_bus.set_total_progress_reset.connect(self.reset_total_progress)

        self._signal_bus.set_detail_progress_current.connect(self.set_detail_progress_value)
        self._signal_bus.set_detail_progress_max.connect(self.set_detail_progress_max)
        self._signal_bus.advance_detail_progress.connect(self.advance_detail_progress)
        self._signal_bus.set_detail_progress_description.connect(self.set_detail_progress_description)
        self._signal_bus.set_detail_progress_finish.connect(self.finish_detail_progress)
        self._signal_bus.set_detail_progress_reset.connect(self.reset_detail_progress)

    def get_video_file_list(self) -> DraggableListWidget:
        return self.ui.listWidget

    def get_select_video_btn(self) -> PushButton:
        return self.ui.PushButton

    def get_vertical_video_radio_btn(self) -> RadioButton:
        return self.ui.RadioButton_2

    def get_horization_video_radio_btn(self) -> RadioButton:
        return self.ui.RadioButton

    def get_rotate_video_cb(self) -> ComboBox:
        return self.ui.ComboBox_2

    def get_preview_mode_segmented_widget(self) -> SegmentedWidget:
        return self.ui.SegmentedWidget

    def get_preview_stack_widget(self) -> QStackedWidget:
        return self.ui.stackedWidget

    def get_preview_pic_lb(self) -> QLabel:
        return self.ui.label

    def get_clockwise_rotate_btn(self) -> PushButton:
        return self.ui.PushButton_2

    def get_counterclockwise_rotate_btn(self) -> PushButton:
        return self.ui.PushButton_3

    def get_upside_down_rotate_btn(self) -> PushButton:
        return self.ui.PushButton_4

    def get_video_widget(self) -> QWidget:
        return self.ui.page_2

    def get_video_player(self) -> VideoWidget:
        self.video_widget = VideoWidget()
        # 先清除之前的播放器
        for i in range(self.get_video_widget().layout().count()):
            self.get_video_widget().layout().itemAt(i).widget().deleteLater()
        self.get_video_widget().layout().addWidget(self.video_widget)
        return self.video_widget

    def get_total_progress_bar(self) -> ProgressBar:
        return self.ui.ProgressBar_2

    def get_total_progress_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_2

    def get_total_progress_current_value_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_4

    def get_total_progress_total_value_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_6

    def get_total_progress_percent_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_8

    def get_detail_progress_bar(self) -> ProgressBar:
        return self.ui.ProgressBar

    def get_detail_progress_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_3

    def get_detail_progress_current_value_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_5

    def get_detail_progress_total_value_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_7

    def get_detail_progress_percent_lb(self) -> BodyLabel:
        return self.ui.BodyLabel_9

    def get_start_btn(self) -> PrimaryPushButton:
        return self.ui.PrimaryPushButton

    # 进度条相关
    def set_total_progress_value(self, value: int):
        self.get_total_progress_bar().setValue(value)
        self._current_total_progress_value = value
        self.get_total_progress_bar().update()
        self.update_total_progress_percent()

    def set_detail_progress_value(self, value: int):
        self.get_detail_progress_bar().setValue(value)
        self._current_detail_progress_value = value
        self.get_detail_progress_bar().update()
        self.update_detail_progress_percent()

    def set_total_progress_max(self, value: int):
        self.get_total_progress_bar().setMaximum(value)
        self.get_total_progress_total_value_lb().setText(str(value))
        self._current_total_progress_max = value
        self.get_total_progress_bar().update()
        self.update_total_progress_percent()

    def set_detail_progress_max(self, value: int):
        self.get_detail_progress_bar().setMaximum(value)
        self.get_detail_progress_total_value_lb().setText(str(value))
        self._current_detail_progress_max = value
        self.get_detail_progress_bar().update()
        self.update_detail_progress_percent()

    def advance_total_progress(self, value: int):
        if self._current_total_progress_value + value > self._current_total_progress_max:
            return
        self._current_total_progress_value = self._current_total_progress_value + value
        self.get_total_progress_bar().setValue(self._current_total_progress_value)
        self.get_total_progress_bar().update()
        self.update_total_progress_percent()

    def advance_detail_progress(self, value: int):
        if self._current_detail_progress_value + value > self._current_detail_progress_max:
            return
        self._current_detail_progress_value = self._current_detail_progress_value + value
        self.get_detail_progress_bar().setValue(self._current_detail_progress_value)
        self.get_detail_progress_bar().update()
        self.update_detail_progress_percent()

    def set_total_progress_description(self, description: str):
        self._current_detail_progress_description = description
        self.get_total_progress_lb().setText(description)
        self.get_total_progress_bar().update()

    def set_detail_progress_description(self, description: str):
        self._current_detail_progress_description = description
        self.get_detail_progress_lb().setText(description)
        self.get_detail_progress_bar().update()

    def finish_total_progress(self):
        self.get_total_progress_bar().setValue(self._current_total_progress_max)
        self.get_total_progress_bar().update()
        self.update_total_progress_percent()

    def finish_detail_progress(self):
        self.get_detail_progress_bar().setValue(self._current_detail_progress_max)
        self.get_detail_progress_bar().update()
        self.update_detail_progress_percent()

    def reset_total_progress(self):
        self.set_total_progress_max(0)
        self.set_total_progress_value(0)
        self.get_total_progress_bar().update()
        self.update_total_progress_percent()

    def reset_detail_progress(self):
        self.set_detail_progress_max(0)
        self.set_detail_progress_value(0)
        self.get_detail_progress_bar().update()
        self.update_detail_progress_percent()

    def update_total_progress_percent(self):
        current_value: int = self._current_total_progress_value
        max_value: int = max(self._current_total_progress_max, 1)
        self.get_total_progress_percent_lb().setText(f"{min(current_value / max_value, 100):.2%}")
        self.get_total_progress_current_value_lb().setText(str(min(current_value, max_value)))

    def update_detail_progress_percent(self):
        current_value: int = self._current_detail_progress_value
        max_value: int = max(self._current_detail_progress_max, 1)
        self.get_detail_progress_percent_lb().setText(f"{min(current_value / max_value, 100):.2%}")
        self.get_detail_progress_current_value_lb().setText(str(min(current_value, max_value)))

    def _initialize(self) -> None:
        def on_preview_image():
            stack = self.get_preview_stack_widget()
            stack.setCurrentIndex(0)

        def on_preview_video():
            stack = self.get_preview_stack_widget()
            stack.setCurrentIndex(1)

        # 初始化SegmentedWidget
        sg: SegmentedWidget = self.get_preview_mode_segmented_widget()
        sg.insertItem(0, "image", "预览图片", onClick=lambda: on_preview_image())
        sg.insertItem(1, "video", "预览视频", onClick=lambda: on_preview_video())
        sg.setCurrentItem("image")
        stack = self.get_preview_stack_widget()
        stack.setCurrentIndex(0)

        # 初始化视频播放器
        self.video_widget = VideoWidget()
        self.get_video_widget().layout().addWidget(self.video_widget)

        # 初始化旋转下拉框
        cb: ComboBox = self.get_rotate_video_cb()
        cb.addItems(self._rotation2cn.values())
        cb.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication([])
    window = ConcateView()
    window.show()
    app.exec()

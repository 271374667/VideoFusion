import re

import loguru
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QLabel, QStackedWidget, QWidget
from qfluentwidgets import Action, FluentIcon, MenuAnimationType
from qfluentwidgets.components import (BodyLabel, ComboBox, PrimaryPushButton, ProgressBar, PushButton,
                                       RadioButton, RoundMenu, SegmentedWidget)
from qfluentwidgets.multimedia import VideoWidget

from src.components.sort_tool_component import DraggableListWidget
from src.core.enums import Rotation
from src.interface.Ui_concate_page import Ui_Form

WINDOW_RENAME_FILE_REGEX = re.compile(r'.*?\((\d+)\)\..*?')
TIME_FILE_REGEX = re.compile(r'.*?([1-2]\d{3}).([0-1]\d).([0-3]\d).*?')


class ConcateView(QWidget):
    def __init__(self):
        super().__init__()

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

    def _initialize_video_list(self) -> None:
        # 当右键点击时，显示自定义的上下文菜单
        def show_context_menu(point):
            global_pos = self.get_video_file_list().mapToGlobal(point)
            self.list_menu.exec(global_pos, aniType=MenuAnimationType.FADE_IN_DROP_DOWN)

        def sortAscending():
            list_widget = self.get_video_file_list()
            data = list_widget.get_all_items()
            # 判断文件是否都是数字,如果是数字则按数字排序,否则按字符串排序
            if all(x.isdigit() for x in data):
                data.sort(key=int)
                list_widget.set_items(data)
                loguru.logger.debug(f"按数字排序{len(data)}个文件")
            # 判断文件是否符合window重命名规则,如果符合则按数字排序,例如1(1).mp4, 1(20).mp4, 1(300).mp4
            elif all(WINDOW_RENAME_FILE_REGEX.match(x) for x in data):
                data.sort(key=lambda x: int(WINDOW_RENAME_FILE_REGEX.search(x).group(1)))
                list_widget.set_items(data)
                loguru.logger.debug(f"按window重命名规则排序{len(data)}个文件")
            # 判断文件是否都是日期,如果是日期则按日期排序
            elif all(TIME_FILE_REGEX.match(x) for x in data):
                data.sort(key=lambda x: (
                        int(TIME_FILE_REGEX.search(x).group(1)),
                        int(TIME_FILE_REGEX.search(x).group(2),
                            int(TIME_FILE_REGEX.search(x).group(3))
                            )
                        )
                          )
                list_widget.set_items(data)
                loguru.logger.debug(f"按日期排序{len(data)}个文件")
            else:
                list_widget.set_items(sorted(data))
                loguru.logger.debug(f"按字符串排序{len(data)}个文件")

        def sortDescending():
            list_widget = self.get_video_file_list()
            data = list_widget.get_all_items()
            # 判断文件是否都是数字,如果是数字则按数字排序,否则按字符串排序
            if all(x.isdigit() for x in data):
                data.sort(key=int, reverse=True)
                list_widget.set_items(data)
                loguru.logger.debug(f"按数字倒序排序{len(data)}个文件")
            # 判断文件是否符合window重命名规则,如果符合则按数字排序,例如1(1).mp4, 1(2).mp4, 1(3).mp4
            elif all(WINDOW_RENAME_FILE_REGEX.match(x) for x in data):
                data.sort(key=lambda x: int(WINDOW_RENAME_FILE_REGEX.search(x).group(1)), reverse=True)
                list_widget.set_items(data)
                loguru.logger.debug(f"按window重命名规则倒序排序{len(data)}个文件")
                loguru.logger.debug(f"按日期倒序排序{len(data)}个文件")
            # 判断文件是否都是日期,如果是日期则按日期排序
            elif all(TIME_FILE_REGEX.match(x) for x in data):
                data.sort(reverse=True, key=lambda x: (
                        int(TIME_FILE_REGEX.search(x).group(1)),
                        int(TIME_FILE_REGEX.search(x).group(2),
                            int(TIME_FILE_REGEX.search(x).group(3))
                            )
                        )
                          )
                list_widget.set_items(data)
            else:
                list_widget.set_items(sorted(data, reverse=True))
                loguru.logger.debug(f"按字符串倒序排序{len(data)}个文件")

        # 初始化视频列表框的右键菜单
        self.list_menu = RoundMenu(self.get_video_file_list())
        self.asc_action = Action()
        self.asc_action.setIcon(FluentIcon.UP)
        self.asc_action.setText("升序")
        self.asc_action.triggered.connect(sortAscending)
        self.desc_action = Action()
        self.desc_action.setIcon(FluentIcon.DOWN)
        self.desc_action.setText("降序")
        self.desc_action.triggered.connect(sortDescending)
        self.move2top_action = Action()
        self.move2top_action.setIcon(FluentIcon.MARKET)
        self.move2top_action.setText("置顶")
        self.move2bottom_action = Action()
        self.move2bottom_action.setIcon(FluentIcon.REMOVE)
        self.move2bottom_action.setText("置底")
        self.clear_list_action = Action()
        self.clear_list_action.setIcon(FluentIcon.DELETE)
        self.clear_list_action.setText("清空")
        self.export_list_action = Action()
        self.export_list_action.setIcon(FluentIcon.EMBED)
        self.export_list_action.setText("导出为txt")
        self.import_list_action = Action()
        self.import_list_action.setIcon(FluentIcon.CLOUD_DOWNLOAD)
        self.import_list_action.setText("导入txt")

        self.list_menu.addAction(self.asc_action)
        self.list_menu.addAction(self.desc_action)
        self.list_menu.addAction(self.move2top_action)
        self.list_menu.addAction(self.move2bottom_action)
        self.list_menu.addAction(self.clear_list_action)
        self.list_menu.addSeparator()
        self.list_menu.addAction(self.export_list_action)
        self.list_menu.addAction(self.import_list_action)
        self.video_list = self.get_video_file_list()
        self.video_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.video_list.customContextMenuRequested.connect(show_context_menu)

    def _initialize(self) -> None:
        def on_preview_image():
            stack = self.get_preview_stack_widget()
            stack.setCurrentIndex(0)

        def on_preview_video():
            stack = self.get_preview_stack_widget()
            stack.setCurrentIndex(1)

        # 初始化视频列表
        self._initialize_video_list()

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

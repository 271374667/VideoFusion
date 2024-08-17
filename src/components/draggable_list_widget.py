import re
from pathlib import Path

import loguru
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QKeyEvent
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFileDialog, QListWidget, QListWidgetItem, QMenu,
                               QVBoxLayout, QWidget)
from qfluentwidgets import Action, FluentIcon, MenuAnimationType
from qfluentwidgets.components import RoundMenu
from src import settings
from src import utils
from src.signal_bus import SignalBus

signal_bus = SignalBus()
WINDOW_RENAME_FILE_REGEX = re.compile(r'.*?\((\d+)\)\..*?')
TIME_FILE_REGEX = re.compile(r'.*?([1-2]\d{3}).([0-1]\d).([0-3]\d).*?')


class DraggableListWidgetView(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.video_suffix: list[str] = settings.AVAILABLE_VIDEO_SUFFIX

    def get_all_items(self) -> list[str]:
        return [self.item(i).text() for i in range(self.count())]

    def set_items(self, items: list[str]) -> None:
        self.clear()
        for item in items:
            self.addFileItem(item)

    def addFileItem(self, file_path: str) -> None:
        item = QListWidgetItem(file_path)
        self.addItem(item)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if file_path := url.toLocalFile():
                    # 判断是否是txt文件,如果是则读取文件内的路径
                    if file_path.endswith('.txt'):
                        txt = Path(file_path).read_text(encoding='utf-8').splitlines()
                        for line in txt:
                            if not utils.is_available_video_file(line):
                                loguru.logger.error(f"拖拽添加了一个不支持的文件: {line.strip()}")
                                continue
                            self.addFileItem(line.strip().replace('"', ''))  # 去除引号
                            signal_bus.file_droped.emit(line.strip())
                            loguru.logger.debug(f"拖拽添加了一个文件: {line.strip()}")
                    elif file_path.endswith(tuple(self.video_suffix)):
                        if not utils.is_available_video_file(file_path):
                            loguru.logger.error(f"拖拽添加了一个不支持的文件: {file_path}")
                            continue
                        self.addFileItem(file_path)
                        signal_bus.file_droped.emit(file_path)
                        loguru.logger.debug(f"拖拽添加了一个文件: {file_path}")
                    else:
                        loguru.logger.error(f"拖拽添加了一个不支持的文件: {file_path}")
                        loguru.logger.debug(f"支持的视频格式: {self.video_suffix},以及一行一个视频文件的txt文件，同时确保文件大小大于{settings.READABLEVIDEOSIZE}kb")
            self.sortItems(Qt.SortOrder.AscendingOrder)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Control:
            self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        if event.key() in [Qt.Key.Key_Backspace, Qt.Key.Key_Delete]:
            if current_item := self.currentItem():
                row = self.row(current_item)
                self.takeItem(row)
                loguru.logger.debug(f"删除了一个文件: {current_item.text()}")

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Control:
            self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        super().keyReleaseEvent(event)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        del_action = QAction('删除', self)
        context_menu.addAction(del_action)
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == del_action:
            if current_item := self.currentItem():
                row = self.row(current_item)
                self.takeItem(row)
                loguru.logger.debug(f"右键删除了一个文件: {current_item.text()}")


class DraggableListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.sort_message: str = "自动排序支持下列形式: 数字, window重命名后缀, 日期,如果均无法匹配则使用字符串排序"
        self._list_widget = DraggableListWidgetView()

        # 初始化视频列表框的右键菜单
        self.list_menu = RoundMenu(self._list_widget)
        self.asc_action = Action()
        self.asc_action.setIcon(FluentIcon.UP)
        self.asc_action.setText("升序")
        self.asc_action.triggered.connect(self.sortAscending)
        self.desc_action = Action()
        self.desc_action.setIcon(FluentIcon.DOWN)
        self.desc_action.setText("降序")
        self.desc_action.triggered.connect(self.sortDescending)
        self.move2top_action = Action()
        self.move2top_action.setIcon(FluentIcon.MARKET)
        self.move2top_action.setText("置顶")
        self.move2top_action.triggered.connect(self.moveToTop)
        self.move2bottom_action = Action()
        self.move2bottom_action.setIcon(FluentIcon.REMOVE)
        self.move2bottom_action.setText("置底")
        self.move2bottom_action.triggered.connect(self.moveToBottom)
        self.remove_action = Action()
        self.remove_action.setIcon(FluentIcon.CLOSE)
        self.remove_action.setText("删除")
        self.remove_action.triggered.connect(self.removeCurrent)

        self.clear_list_action = Action()
        self.clear_list_action.setIcon(FluentIcon.DELETE)
        self.clear_list_action.setText("清空")
        self.clear_list_action.triggered.connect(self.clearList)
        self.export_list_action = Action()
        self.export_list_action.setIcon(FluentIcon.EMBED)
        self.export_list_action.setText("导出为txt")
        self.export_list_action.triggered.connect(self.exportToFile)
        self.import_list_action = Action()
        self.import_list_action.setIcon(FluentIcon.CLOUD_DOWNLOAD)
        self.import_list_action.setText("导入txt")
        self.import_list_action.triggered.connect(self.importFromFile)

        self.list_menu.addAction(self.asc_action)
        self.list_menu.addAction(self.desc_action)
        self.list_menu.addAction(self.move2top_action)
        self.list_menu.addAction(self.move2bottom_action)
        self.list_menu.addAction(self.remove_action)
        self.list_menu.addAction(self.clear_list_action)
        self.list_menu.addSeparator()
        self.list_menu.addAction(self.export_list_action)
        self.list_menu.addAction(self.import_list_action)

        self._list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list_widget.customContextMenuRequested.connect(self.show_context_menu)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self._list_widget)
        self.setLayout(self.main_layout)

    def get_draggable_list_view(self) -> DraggableListWidgetView:
        return self._list_widget

    def get_current_item_text(self) -> str:
        if self._list_widget.currentItem():
            return self._list_widget.currentItem().text()
        return ""

    def currentItem(self) -> QListWidgetItem:
        return self._list_widget.currentItem()

    def add_items(self, items: list[str]) -> None:
        for item in items:
            self._list_widget.addFileItem(item)

    def set_items(self, items: list[str]) -> None:
        self._list_widget.set_items(items)

    def show_context_menu(self, point):
        global_pos = self._list_widget.mapToGlobal(point)
        self.list_menu.exec(global_pos, aniType=MenuAnimationType.FADE_IN_DROP_DOWN)

    def sortAscending(self):
        data = self._list_widget.get_all_items()
        # 判断文件是否都是数字,如果是数字则按数字排序,否则按字符串排序
        if all(x.isdigit() for x in data):
            data.sort(key=int)
            self._list_widget.set_items(data)
            loguru.logger.debug(f"按数字排序{len(data)}个文件")
        # 判断文件是否符合window重命名规则,如果符合则按数字排序,例如1(1).mp4, 1(20).mp4, 1(300).mp4
        elif all(WINDOW_RENAME_FILE_REGEX.match(x) for x in data):
            data.sort(key=lambda x: int(WINDOW_RENAME_FILE_REGEX.search(x).group(1)))
            self._list_widget.set_items(data)
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
            self._list_widget.set_items(data)
            loguru.logger.debug(f"按日期排序{len(data)}个文件")
        else:
            self._list_widget.set_items(sorted(data))
            loguru.logger.debug(f"按字符串排序{len(data)}个文件")

    def sortDescending(self):
        data = self._list_widget.get_all_items()
        # 判断文件是否都是数字,如果是数字则按数字排序,否则按字符串排序
        if all(x.isdigit() for x in data):
            data.sort(key=int, reverse=True)
            self._list_widget.set_items(data)
            loguru.logger.debug(f"按数字倒序排序{len(data)}个文件")
        # 判断文件是否符合window重命名规则,如果符合则按数字排序,例如1(1).mp4, 1(2).mp4, 1(3).mp4
        elif all(WINDOW_RENAME_FILE_REGEX.match(x) for x in data):
            data.sort(key=lambda x: int(WINDOW_RENAME_FILE_REGEX.search(x).group(1)), reverse=True)
            self._list_widget.set_items(data)
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
            self._list_widget.set_items(data)
        else:
            self._list_widget.set_items(sorted(data, reverse=True))
            loguru.logger.debug(f"按字符串倒序排序{len(data)}个文件")

    def moveToTop(self):
        if current_item := self._list_widget.currentItem():
            current_row = self._list_widget.row(current_item)
            self._list_widget.takeItem(current_row)
            self._list_widget.insertItem(0, current_item)
            self._list_widget.setCurrentItem(current_item)

    def moveToBottom(self):
        if current_item := self._list_widget.currentItem():
            current_row = self._list_widget.row(current_item)
            self._list_widget.takeItem(current_row)
            self._list_widget.addItem(current_item)
            self._list_widget.setCurrentItem(current_item)

    def clearList(self):
        self._list_widget.clear()

    def removeCurrent(self):
        if current_item := self._list_widget.currentItem():
            row = self._list_widget.row(current_item)
            self._list_widget.takeItem(row)
            loguru.logger.debug(f"删除了一个文件: {current_item.text()}")

    def importFromFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r') as file:
                for line in file:
                    self._list_widget.addFileItem(line.strip())
                    loguru.logger.debug(f"导入文件: {line.strip()}")

    def exportToFile(self):
        current_select_video = self._list_widget.currentItem().text()
        target_dir = "sort_index.txt"
        if Path(current_select_video).is_file():
            target_dir = str(Path(current_select_video).with_name("sort_index.txt"))

        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", target_dir, "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as file:
                for i in range(self._list_widget.count()):
                    file.write(self._list_widget.item(i).text() + '\n')
                    loguru.logger.debug(f"导出文件: {self._list_widget.item(i).text()}")

    def setFrameShape(self, shape):
        self._list_widget.setFrameShape(shape)

    def setFrameShadow(self, shadow):
        self._list_widget.setFrameShadow(shadow)

    def setLineWidth(self, width):
        self._list_widget.setLineWidth(width)

    def setMidLineWidth(self, width):
        self._list_widget.setMidLineWidth(width)

    def setDragEnabled(self, enable):
        self._list_widget.setDragEnabled(enable)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    widget = DraggableListWidget()
    widget.show()
    sys.exit(app.exec())

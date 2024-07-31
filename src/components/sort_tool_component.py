import random
import re

import cv2
import loguru
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QImage, QKeyEvent, QPixmap, QTransform
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFileDialog, QHBoxLayout, QLabel,
                               QListWidget, QListWidgetItem, QMenu, QPushButton, QSpacerItem, QVBoxLayout, QWidget)

WINDOW_RENAME_FILE_REGEX = re.compile(r'.*?\((\d+)\)\..*?')
TIME_FILE_REGEX = re.compile(r'.*?([1-2]\d{3}).([0-1]\d).([0-3]\d).*?')


class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.video_suffix: list[str] = ['.mp4', '.avi', '.mov', '.flv', '.mkv', '.rmvb', '.wmv', '.webm', '.ts', '.m4v']

    def get_all_items(self) -> list[str]:
        return [self.item(i).text() for i in range(self.count())]

    def set_items(self, items: list[str]) -> None:
        self.clear()
        for item in items:
            self.addFileItem(item)

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
                        with open(file_path, 'r') as file:
                            for line in file:
                                self.addFileItem(line.strip())
                                loguru.logger.debug(f"拖拽添加了一个文件: {line.strip()}")
                    elif file_path.endswith(tuple(self.video_suffix)):
                        self.addFileItem(file_path)
                        loguru.logger.debug(f"拖拽添加了一个文件: {file_path}")
            self.sortItems(Qt.SortOrder.AscendingOrder)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def addFileItem(self, file_path: str) -> None:
        item = QListWidgetItem(file_path)
        self.addItem(item)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Control:
            self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
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


class SortToolComponent(QWidget):
    def __init__(self):
        super().__init__()
        sort_message: str = "自动排序支持下列形式: 数字, window重命名后缀, 日期,如果均无法匹配则使用字符串排序"
        self.current_rotation: int = 0
        self._black_remover = BlackRemover()

        self.resize(830, 500)
        self.setWindowTitle("拖拽视频文件排序生成工具")

        self._main_layout = QVBoxLayout()
        self._asc_btn = QPushButton("升序")
        self._asc_btn.setToolTip(sort_message)
        self._desc_btn = QPushButton("降序")
        self._desc_btn.setToolTip(sort_message)
        self._top_btn = QPushButton("置顶")
        self._bottom_btn = QPushButton("置底")
        self._clear_btn = QPushButton("清空")
        # 从txt文件导入文件路径到列表内,每个文件路径占一行
        self._import_btn = QPushButton("导入")
        # 将列表内的文件导出到txt文件里,每个文件路径占一行
        self._export_btn = QPushButton("导出")
        # 使用cv2读取视频文件的第一帧,并显示在此处
        self._first_img_btn = QPushButton("第一帧")
        # 使用cv2读取视频文件的最后一帧,并显示在此处
        self._last_img_btn = QPushButton("最后一帧")
        # 使用cv2和random读取视频文件的随机一帧,并显示在此处
        self._random_img_btn = QPushButton("随机帧")
        self._img_clockwise_btn = QPushButton("顺时针旋转")
        self._img_counterclockwise_btn = QPushButton("逆时针旋转")
        self._img_upside_down_btn = QPushButton("上下翻转")
        self._black_remove_cb = QCheckBox("去除黑边")
        self._vspacer = QSpacerItem(20, 100)
        # 使用cv2读取视频文件的第一帧,并显示在此处
        self._img = QLabel("此处将显示图片")
        self._img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 设置图片能够自适应大小
        self._img.setScaledContents(True)
        self._list_widget = DraggableListWidget()
        self._list_widget.setMaximumWidth(400)

        # 提示信息
        self._list_label = QLabel(
                f"请拖拽(视频文件/包含路径的txt文件)到左侧的列表中\n"
                f"列表本身支持拖拽排序,右键删除,按住Ctrl多选\n"
                f"目前支持的视频文件格式: {', '.join(self._list_widget.video_suffix)}")
        self._list_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._list_btn_layout = QHBoxLayout()
        self._list_btn_layout.addWidget(self._asc_btn)
        self._list_btn_layout.addWidget(self._desc_btn)
        self._list_btn_layout.addWidget(self._top_btn)
        self._list_btn_layout.addWidget(self._bottom_btn)
        self._list_btn_layout.addWidget(self._clear_btn)

        self._list_btn_second_layout = QHBoxLayout()
        self._list_btn_second_layout.addWidget(self._import_btn)
        self._list_btn_second_layout.addWidget(self._export_btn)

        self._list_layout = QVBoxLayout()
        self._list_layout.addWidget(self._list_widget)
        self._list_layout.addLayout(self._list_btn_layout)
        self._list_layout.addLayout(self._list_btn_second_layout)

        self._img_btn_layout = QHBoxLayout()
        self._img_btn_layout.addWidget(self._first_img_btn)
        self._img_btn_layout.addWidget(self._last_img_btn)
        self._img_btn_layout.addWidget(self._random_img_btn)

        self._img_btn_second_layout = QHBoxLayout()
        self._img_btn_second_layout.addWidget(self._img_clockwise_btn)
        self._img_btn_second_layout.addWidget(self._img_counterclockwise_btn)
        self._img_btn_second_layout.addWidget(self._img_upside_down_btn)
        self._img_btn_second_layout.addWidget(self._black_remove_cb)

        self._img_layout = QVBoxLayout()
        self._img_layout.addWidget(self._img)
        self._img_layout.addItem(self._vspacer)
        self._img_layout.addLayout(self._img_btn_layout)
        self._img_layout.addLayout(self._img_btn_second_layout)

        self._content_layout = QHBoxLayout()
        self._content_layout.addLayout(self._list_layout)
        self._content_layout.addLayout(self._img_layout)

        self._main_layout.addWidget(self._list_label)
        self._main_layout.addLayout(self._content_layout)
        self.setLayout(self._main_layout)

        self._asc_btn.clicked.connect(self.sortAscending)
        self._desc_btn.clicked.connect(self.sortDescending)
        self._top_btn.clicked.connect(self.moveToTop)
        self._bottom_btn.clicked.connect(self.moveToBottom)
        self._clear_btn.clicked.connect(self.clearList)
        self._import_btn.clicked.connect(self.importFromFile)
        self._export_btn.clicked.connect(self.exportToFile)
        self._first_img_btn.clicked.connect(self.showFirstFrame)
        self._last_img_btn.clicked.connect(self.showLastFrame)
        self._random_img_btn.clicked.connect(self.showRandomFrame)
        self._list_widget.clicked.connect(self.showFirstFrame)
        self._img_clockwise_btn.clicked.connect(self.rotateClockwise)
        self._img_counterclockwise_btn.clicked.connect(self.rotateCounterclockwise)
        self._img_upside_down_btn.clicked.connect(self.rotateUpsideDown)
        self._black_remove_cb.stateChanged.connect(self.showFirstFrame)

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
        self._img.clear()
        self._img.setText("此处将显示图片")

    def importFromFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r') as file:
                for line in file:
                    self._list_widget.addFileItem(line.strip())
                    loguru.logger.debug(f"导入文件: {line.strip()}")

    def exportToFile(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as file:
                for i in range(self._list_widget.count()):
                    file.write(self._list_widget.item(i).text() + '\n')
                    loguru.logger.debug(f"导出文件: {self._list_widget.item(i).text()}")

    def showFirstFrame(self):
        if not (current_item := self._list_widget.currentItem()):
            return
        video_path = current_item.text()
        cap = cv2.VideoCapture(video_path)
        # 显示视频中不为黑色的第一帧
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if not self._black_remover.is_black(frame):
                break
        self._show_frame_on_label(cap, '显示第一帧: ', video_path)

    def showLastFrame(self):
        if current_item := self._list_widget.currentItem():
            video_path = current_item.text()
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
            self._show_frame_on_label(cap, '显示最后一帧: ', video_path)

    def showRandomFrame(self):
        if current_item := self._list_widget.currentItem():
            video_path = current_item.text()
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, random.randint(0, total_frames - 1))
            self._show_frame_on_label(cap, '显示随机帧: ', video_path)

    def _show_frame_on_label(self, cap, arg1, video_path):
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cap.release()
        if ret:
            self._set_img(frame)
            loguru.logger.debug(f"{arg1}{video_path}")

    def rotateClockwise(self):
        # 先检查是否有图片
        if self._img.pixmap():
            self.current_rotation = (self.current_rotation + 90) % 360
            self._rotate_img(90, '顺时针旋转图片, 当前角度: ')

    def rotateCounterclockwise(self):
        # 先检查是否有图片
        if self._img.pixmap():
            self.current_rotation = (self.current_rotation - 90) % 360
            self._rotate_img(-90, '逆时针旋转图片, 当前角度: ')

    def rotateUpsideDown(self):
        # 先检查是否有图片
        if self._img.pixmap():
            self.current_rotation = (self.current_rotation + 180) % 360
            self._rotate_img(180, '上下翻转图片, 当前角度: ')

    def _rotate_img(self, angle, log_title):
        pixmap = self._img.pixmap()
        pixmap = pixmap.transformed(QTransform().rotate(angle))
        self._img.setPixmap(pixmap)
        loguru.logger.debug(f"{log_title}{self.current_rotation}")

    def _set_img(self, frame):
        # 是否启用去除黑边

        img = QImage(frame._file_path, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        # 剪裁图片
        if self._black_remove_cb.isChecked():
            left_top_x, left_top_y, right_bottom_x, right_bottom_y = self._black_remover.start(img_array=frame)
            img = img.copy(left_top_x, left_top_y, right_bottom_x - left_top_x, right_bottom_y - left_top_y)

        # 旋转图片
        img = img.transformed(QTransform().rotate(self.current_rotation))

        # 将图片缩放到QLabel的大小
        img = img.scaled(self._img.width(), self._img.height())
        self._img.setPixmap(QPixmap.fromImage(img))

    # 缩放窗口的时候,图片也会自适应大小
    def resizeEvent(self, event):
        if self._img.pixmap():
            self._img.setMaximumSize(QSize(self.width() // 2, self.height() // 2))
            pixmap = self._img.pixmap()
            pixmap = pixmap.scaled(self._img.width(), self._img.height(), Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self._img.setPixmap(pixmap)
        event.accept()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    widget = SortToolComponent()
    widget.show()
    sys.exit(app.exec())

from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLineEdit

from src.signal_bus import SignalBus

signal_bus = SignalBus()


class FileDragAndDropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            # 如果不是文件夹路径，或者不是txt文件，就不接受
            if not url.isLocalFile() or not url.fileName().endswith('.txt'):
                return
            self.setText(url.toLocalFile())
            signal_bus.file_droped.emit(url.toLocalFile())
            event.acceptProposedAction()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    window = FileDragAndDropLineEdit()
    window.show()
    app.exec()

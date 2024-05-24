from PySide6.QtWidgets import QApplication, QWidget

from src.interface.Ui_concate_page import Ui_Form


class ConcateView(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QApplication([])
    window = ConcateView()
    window.show()
    app.exec()

from PySide6.QtWidgets import QApplication

from src.presenter.home_presenter import HomePresenter

if __name__ == '__main__':
    app = QApplication([])
    home_presenter = HomePresenter()
    home_presenter.get_view().show()
    app.exec()

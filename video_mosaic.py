from PySide6.QtWidgets import QApplication

from src.presenter.main_presenter import MainPresenter

if __name__ == '__main__':
    app = QApplication([])
    main_presenter = MainPresenter()
    main_presenter.get_view().show()
    app.exec()

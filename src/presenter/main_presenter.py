from src.presenter.concate_presenter import ConcatePresenter
from src.presenter.settings_presenter import SettingsPresenter
from src.view.main_view import MainView


class MainPresenter:
    def __init__(self):
        self._concate_presenter = ConcatePresenter()
        self._settings_presenter = SettingsPresenter()

        self._view = MainView(
                self._concate_presenter.get_view(),
                self._settings_presenter.get_view()
                )

    def get_view(self) -> MainView:
        return self._view


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    m = MainPresenter()
    m.get_view().show()
    app.exec()

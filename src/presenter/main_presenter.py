from src.presenter.concate_presenter import ConcatePresenter
from src.presenter.settings_presenter import SettingsPresenter
from src.signal_bus import SignalBus
from src.view.main_view import MainView


class MainPresenter:
    def __init__(self):
        self._signal_bus = SignalBus()
        self._concate_presenter = ConcatePresenter()
        self._settings_presenter = SettingsPresenter()

        self._view = MainView(
                self._concate_presenter.get_view(),
                self._settings_presenter.get_view()
                )

        # 开始运行之后禁用设置界面
        self._signal_bus.started.connect(self.disable_settings_view)
        self._signal_bus.finished.connect(self.enable_settings_view)

    def get_view(self) -> MainView:
        return self._view

    def enable_settings_view(self):
        self._settings_presenter.get_view().setEnabled(True)

    def disable_settings_view(self):
        self._settings_presenter.get_view().setEnabled(False)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    m = MainPresenter()
    m.get_view().show()
    app.exec()

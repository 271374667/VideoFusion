import loguru
from PySide6.QtWidgets import QApplication

from src.core.paths import LOG_FILE
from src.presenter.main_presenter import MainPresenter

loguru.logger.add(LOG_FILE, rotation="1 week", retention="1 days", level="DEBUG")


def main():
    try:
        app = QApplication([])
        main_presenter = MainPresenter()
        main_presenter.get_view().show()
        app.exec()
    except Exception as e:
        loguru.logger.critical(f"程序发生了未知错误: {e}")


if __name__ == '__main__':
    main()

from PySide6.QtCore import QObject, Signal

from src.utils import singleton


@singleton
class SignalBus(QObject):
    started = Signal()
    finished = Signal()
    failed = Signal()
    set_running = Signal(bool)

    file_droped = Signal(str)

    set_total_progress_current = Signal(int)
    set_total_progress_max = Signal(int)
    advance_total_progress = Signal(int)
    set_total_progress_description = Signal(str)
    set_total_progress_finish = Signal()
    set_total_progress_reset = Signal()

    set_detail_progress_current = Signal(int)
    set_detail_progress_max = Signal(int)
    advance_detail_progress = Signal(int)
    set_detail_progress_description = Signal(str)
    set_detail_progress_finish = Signal()
    set_detail_progress_reset = Signal()

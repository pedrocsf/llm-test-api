from PySide6.QtCore import QElapsedTimer, QObject, QThread, QTimer, Signal

from domain.errors import DomainError
from domain.usecases.prepare_scoring_methods import PrepareScoringMethods

MINIMUM_STARTUP_MILLISECONDS = 5000


class StartupWorker(QThread):
    completed = Signal()
    failed = Signal(str)

    def __init__(self, prepare_scoring_methods: PrepareScoringMethods, parent: QObject | None = None):
        super().__init__(parent)
        self._prepare_scoring_methods = prepare_scoring_methods

    def run(self) -> None:
        try:
            self._prepare_scoring_methods.execute()
        except DomainError as error:
            self.failed.emit(str(error))
        except Exception as error:
            self.failed.emit(f"Unexpected error: {error}")
        else:
            self.completed.emit()


class StartupController(QObject):
    ready = Signal()
    failed = Signal(str)

    def __init__(self, prepare_scoring_methods: PrepareScoringMethods):
        super().__init__()
        self._prepare_scoring_methods = prepare_scoring_methods
        self._worker: StartupWorker | None = None
        self._clock = QElapsedTimer()

    def start(self) -> None:
        if self._worker is not None:
            return
        worker = StartupWorker(self._prepare_scoring_methods, parent=self)
        worker.completed.connect(self._handle_completed)
        worker.failed.connect(self.failed)
        self._worker = worker
        self._clock.start()
        worker.start()

    def _handle_completed(self) -> None:
        remaining_milliseconds = max(0, MINIMUM_STARTUP_MILLISECONDS - self._clock.elapsed())
        QTimer.singleShot(remaining_milliseconds, self.ready.emit)

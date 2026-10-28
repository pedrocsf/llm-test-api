import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from domain.entities.evaluation_request import EvaluationRequest
from domain.entities.evaluation_result import EvaluationResult
from domain.entities.language_model_settings import LanguageModelSettings
from domain.entities.question import Question
from domain.errors import DomainError, EvaluationCancelledError
from domain.scoring.scoring_method import ScoringMethod
from domain.usecases.build_metric_overview import BuildMetricOverview
from domain.usecases.export_result import ExportResult
from domain.usecases.load_questions import LoadQuestions
from domain.usecases.progress import CancellationCheck, ProgressListener
from domain.usecases.rescore_result import RescoreResult
from domain.usecases.run_evaluation import RunEvaluation

MISSING_ENDPOINT_MESSAGE = "Enter the LLM URL."
MISSING_DATASET_MESSAGE = "Load a dataset first."
RUNNING_STATUS = "Running…"
SCORING_STATUS = "Scoring…"
SHUTDOWN_WAIT_MILLISECONDS = 3000

BackgroundTask = Callable[[ProgressListener, CancellationCheck], object]
CompletionHandler = Callable[[object], None]
FailureHandler = Callable[[str], None]


@dataclass(frozen=True)
class EvaluationUseCases:
    load_questions: LoadQuestions
    run_evaluation: RunEvaluation
    rescore_result: RescoreResult
    build_overview: BuildMetricOverview
    export_result: ExportResult


class BackgroundWorker(QThread):
    progressed = Signal(int, int)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, task: BackgroundTask, parent: QObject | None = None):
        super().__init__(parent)
        self._task = task
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        self._cancel_event.set()

    def run(self) -> None:
        try:
            outcome = self._task(self.progressed.emit, self._cancel_event.is_set)
        except EvaluationCancelledError:
            self.cancelled.emit()
        except DomainError as error:
            self.failed.emit(str(error))
        except Exception as error:
            self.failed.emit(f"Unexpected error: {error}")
        else:
            self.completed.emit(outcome)


class EvaluationController(QObject):
    dataset_loaded = Signal(str, int)
    dataset_failed = Signal(str)
    started = Signal(str, bool)
    progressed = Signal(int, int)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    exported = Signal(str)
    export_failed = Signal(str)
    overview_ready = Signal(object)
    overview_failed = Signal(str)

    def __init__(self, use_cases: EvaluationUseCases, scoring_methods: Sequence[ScoringMethod]):
        super().__init__()
        self._use_cases = use_cases
        self._scoring_methods = list(scoring_methods)
        self._selected_method = self._scoring_methods[0]
        self._questions: list[Question] = []
        self._worker: BackgroundWorker | None = None
        self._last_result: EvaluationResult | None = None
        self._is_rescoring = False

    @property
    def scoring_methods(self) -> list[ScoringMethod]:
        return list(self._scoring_methods)

    @property
    def selected_method(self) -> ScoringMethod:
        return self._selected_method

    def load_dataset(self, source: Path) -> None:
        try:
            questions = self._use_cases.load_questions.execute(source)
        except DomainError as error:
            self.dataset_failed.emit(str(error))
            return
        self._questions = questions
        self._last_result = None
        self.dataset_loaded.emit(str(source), len(questions))

    def select_method(self, identifier: str) -> None:
        method = next((candidate for candidate in self._scoring_methods if candidate.identifier == identifier), None)
        if method is None or method is self._selected_method or self._worker is not None:
            return
        self._selected_method = method
        if self._last_result is not None:
            self._launch_rescoring(self._last_result, method)

    def start_evaluation(self, endpoint_url: str, api_key: str, model_name: str) -> None:
        if self._worker is not None:
            return
        if not self._questions:
            self.failed.emit(MISSING_DATASET_MESSAGE)
            return
        if not endpoint_url.strip():
            self.failed.emit(MISSING_ENDPOINT_MESSAGE)
            return
        settings = LanguageModelSettings(
            endpoint_url=endpoint_url.strip(),
            api_key=api_key.strip() or None,
            model_name=model_name.strip() or None,
        )
        request = EvaluationRequest(settings, tuple(self._questions), self._selected_method)
        self._last_result = None
        self._is_rescoring = False
        self._launch_worker(
            lambda on_progress, is_cancelled: self._use_cases.run_evaluation.execute(request, on_progress, is_cancelled),
            self._handle_completed,
            self._handle_failed,
            status_text=RUNNING_STATUS,
            is_cancellable=True,
        )

    def cancel_evaluation(self) -> None:
        if self._worker is not None:
            self._worker.cancel()

    def shutdown(self) -> None:
        worker = self._worker
        if worker is None:
            return
        worker.cancel()
        if not worker.wait(SHUTDOWN_WAIT_MILLISECONDS):
            worker.terminate()
            worker.wait()

    def build_overview(self) -> None:
        if self._worker is not None or self._last_result is None:
            return
        result = self._last_result
        self._launch_worker(
            lambda on_progress, is_cancelled: self._use_cases.build_overview.execute(result, self._scoring_methods),
            self._handle_overview_ready,
            self._handle_overview_failed,
        )

    def export_last_result(self, destination: Path) -> None:
        if self._last_result is None:
            return
        try:
            self._use_cases.export_result.execute(self._last_result, destination)
        except DomainError as error:
            self.export_failed.emit(str(error))
            return
        self.exported.emit(str(destination))

    def _launch_rescoring(self, result: EvaluationResult, method: ScoringMethod) -> None:
        self._is_rescoring = True
        self._launch_worker(
            lambda on_progress, is_cancelled: self._use_cases.rescore_result.execute(result, method, on_progress),
            self._handle_completed,
            self._handle_failed,
            status_text=SCORING_STATUS,
        )

    def _launch_worker(
        self,
        task: BackgroundTask,
        on_completed: CompletionHandler,
        on_failed: FailureHandler,
        status_text: str | None = None,
        is_cancellable: bool = False,
    ) -> None:
        worker = BackgroundWorker(task, parent=self)
        worker.progressed.connect(self.progressed)
        worker.completed.connect(on_completed)
        worker.failed.connect(on_failed)
        worker.cancelled.connect(self.cancelled)
        worker.finished.connect(self._release_worker)
        self._worker = worker
        if status_text is not None:
            self.started.emit(status_text, is_cancellable)
        worker.start()

    def _handle_completed(self, result: EvaluationResult) -> None:
        self._last_result = result
        self._is_rescoring = False
        self.completed.emit(result)

    def _handle_failed(self, message: str) -> None:
        self.failed.emit(message)
        if self._is_rescoring and self._last_result is not None:
            self._is_rescoring = False
            self._selected_method = self._last_result.method
            self.completed.emit(self._last_result)

    def _handle_overview_ready(self, overview: object) -> None:
        self.overview_ready.emit(overview)

    def _handle_overview_failed(self, message: str) -> None:
        self.overview_failed.emit(message)

    def _release_worker(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
        self._worker = None

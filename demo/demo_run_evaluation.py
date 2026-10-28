from collections.abc import Sequence
from datetime import datetime
from time import sleep

from demo.demo_data import DemoEntry
from domain.entities.evaluation_request import EvaluationRequest
from domain.entities.evaluation_result import EvaluationResult
from domain.entities.question_score import QuestionScore
from domain.errors import EvaluationCancelledError
from domain.usecases.progress import CancellationCheck, ProgressListener, ignore_progress, never_cancelled

DEFAULT_STEP_SECONDS = 0.3


class DemoRunEvaluation:
    def __init__(self, entries: Sequence[DemoEntry], step_seconds: float = DEFAULT_STEP_SECONDS):
        self._entries_by_identifier = {entry.identifier: entry for entry in entries}
        self._step_seconds = step_seconds

    def execute(
        self,
        request: EvaluationRequest,
        on_progress: ProgressListener | None = None,
        is_cancelled: CancellationCheck | None = None,
    ) -> EvaluationResult:
        notify_progress = on_progress or ignore_progress
        was_cancelled = is_cancelled or never_cancelled

        scores = []
        for position, question in enumerate(request.questions, start=1):
            if was_cancelled():
                raise EvaluationCancelledError()
            sleep(self._step_seconds)
            entry = self._entries_by_identifier[question.identifier]
            score = request.method.score(question.expected_answer, entry.given_answer)
            scores.append(QuestionScore(question, entry.given_answer, score, entry.response_seconds))
            notify_progress(position, len(request.questions))

        return EvaluationResult(tuple(scores), datetime.now(), request.method)

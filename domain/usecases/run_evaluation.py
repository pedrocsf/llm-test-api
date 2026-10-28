from datetime import datetime
from time import perf_counter

from domain.entities.evaluation_request import EvaluationRequest
from domain.entities.evaluation_result import EvaluationResult
from domain.entities.language_model_settings import LanguageModelSettings
from domain.entities.question_score import QuestionScore
from domain.errors import EvaluationCancelledError
from domain.gateways.language_model_gateway import LanguageModelGateway
from domain.usecases.progress import CancellationCheck, ProgressListener, ignore_progress, never_cancelled


class RunEvaluation:
    def __init__(self, language_model_gateway: LanguageModelGateway):
        self._language_model_gateway = language_model_gateway

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
            given_answer, response_seconds = self._ask_with_timing(request.settings, question.text)
            score = request.method.score(question.expected_answer, given_answer)
            scores.append(QuestionScore(question, given_answer, score, response_seconds))
            notify_progress(position, len(request.questions))

        return EvaluationResult(tuple(scores), datetime.now(), request.method)

    def _ask_with_timing(self, settings: LanguageModelSettings, question_text: str) -> tuple[str, float]:
        started_at = perf_counter()
        given_answer = self._language_model_gateway.ask(settings, question_text)
        return given_answer, perf_counter() - started_at

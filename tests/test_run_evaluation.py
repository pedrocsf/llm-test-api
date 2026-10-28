from datetime import datetime

import pytest

from domain.entities.evaluation_request import EvaluationRequest
from domain.entities.language_model_settings import LanguageModelSettings
from domain.entities.question import Question
from domain.errors import EvaluationCancelledError
from domain.gateways.language_model_gateway import LanguageModelGateway
from domain.scoring.exact_match_scoring_method import ExactMatchScoringMethod
from domain.scoring.scoring_method import ScoreKind, ScoringMethod
from domain.usecases.run_evaluation import RunEvaluation

SETTINGS = LanguageModelSettings(endpoint_url="http://127.0.0.1:1234/v1/chat/completions")


class FakeGateway(LanguageModelGateway):
    def __init__(self):
        self.received_questions = []

    def ask(self, settings, question_text):
        self.received_questions.append(question_text)
        return f"resposta para {question_text}"


class HalfScoringMethod(ScoringMethod):
    identifier = "half"
    display_name = "Half"
    column_header = "Half"
    score_kind = ScoreKind.CONTINUOUS

    def score(self, expected_answer, given_answer):
        return 0.5


def build_request(*questions, method=None):
    return EvaluationRequest(SETTINGS, tuple(questions), method or HalfScoringMethod())


def build_use_case(gateway=None):
    return RunEvaluation(gateway or FakeGateway())


def test_scores_every_question_with_the_requested_method():
    request = build_request(Question("1", "a?", "A"), Question("2", "b?", "B"))

    result = build_use_case().execute(request)

    assert [score.given_answer for score in result.scores] == ["resposta para a?", "resposta para b?"]
    assert result.average_score == 0.5
    assert result.method.identifier == "half"
    assert isinstance(result.evaluated_at, datetime)


def test_uses_the_score_of_the_requested_method():
    request = build_request(Question("1", "a?", "resposta para a?"), method=ExactMatchScoringMethod())

    result = build_use_case().execute(request)

    assert result.scores[0].score == 1.0


def test_measures_response_time_of_each_question(monkeypatch):
    clock = iter([10.0, 10.5, 20.0, 22.0])
    monkeypatch.setattr("domain.usecases.run_evaluation.perf_counter", lambda: next(clock))
    request = build_request(Question("1", "a?", "A"), Question("2", "b?", "B"))

    result = build_use_case().execute(request)

    assert [score.response_seconds for score in result.scores] == [0.5, 2.0]
    assert result.metrics.slowest_response_seconds == 2.0


def test_reports_progress_after_each_question():
    request = build_request(Question("1", "a?", "A"), Question("2", "b?", "B"))
    progress = []

    build_use_case().execute(request, on_progress=lambda completed, total: progress.append((completed, total)))

    assert progress == [(1, 2), (2, 2)]


def test_stops_when_cancelled():
    gateway = FakeGateway()
    request = build_request(Question("1", "a?", "A"), Question("2", "b?", "B"))
    checks = iter([False, True])

    with pytest.raises(EvaluationCancelledError):
        build_use_case(gateway).execute(request, is_cancelled=lambda: next(checks))

    assert gateway.received_questions == ["a?"]

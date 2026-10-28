from datetime import datetime

from domain.entities.evaluation_result import EvaluationResult
from domain.entities.question import Question
from domain.entities.question_score import QuestionScore
from domain.scoring.exact_match_scoring_method import ExactMatchScoringMethod
from domain.scoring.scoring_method import ScoreKind, ScoringMethod
from domain.scoring.token_f1_scoring_method import TokenF1ScoringMethod
from domain.usecases.rescore_result import RescoreResult


class ConstantScoringMethod(ScoringMethod):
    identifier = "constant"
    display_name = "Constant"
    column_header = "Constant"
    score_kind = ScoreKind.CONTINUOUS

    def score(self, expected_answer, given_answer):
        return 0.25


def build_result():
    scores = (
        QuestionScore(Question("1", "Capital?", "Brasília"), "Brasília", 0.9, 1.5),
        QuestionScore(Question("2", "Autor?", "Machado de Assis"), "Machado", 0.4, 0.5),
    )
    return EvaluationResult(scores, datetime(2026, 10, 28, 12, 0, 0), ConstantScoringMethod())


def test_recalculates_scores_with_the_new_method():
    rescored = RescoreResult().execute(build_result(), ExactMatchScoringMethod())

    assert [score.score for score in rescored.scores] == [1.0, 0.0]
    assert rescored.method.identifier == "exact_match"


def test_keeps_answers_response_times_and_date():
    original = build_result()

    rescored = RescoreResult().execute(original, TokenF1ScoringMethod())

    assert [score.given_answer for score in rescored.scores] == ["Brasília", "Machado"]
    assert [score.response_seconds for score in rescored.scores] == [1.5, 0.5]
    assert rescored.evaluated_at == original.evaluated_at


def test_leaves_the_original_result_untouched():
    original = build_result()

    RescoreResult().execute(original, ExactMatchScoringMethod())

    assert [score.score for score in original.scores] == [0.9, 0.4]
    assert original.method.identifier == "constant"


def test_reports_progress_for_each_score():
    progress = []

    RescoreResult().execute(
        build_result(), ConstantScoringMethod(), on_progress=lambda completed, total: progress.append((completed, total))
    )

    assert progress == [(1, 2), (2, 2)]

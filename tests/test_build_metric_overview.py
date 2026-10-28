from datetime import datetime

import pytest

from domain.entities.evaluation_result import EvaluationResult
from domain.entities.question import Question
from domain.entities.question_score import QuestionScore
from domain.scoring.exact_match_scoring_method import ExactMatchScoringMethod
from domain.scoring.scoring_method import ScoreKind, ScoringMethod
from domain.scoring.token_f1_scoring_method import TokenF1ScoringMethod
from domain.usecases.build_metric_overview import BuildMetricOverview


class SourceScoringMethod(ScoringMethod):
    identifier = "source"
    display_name = "Source"
    column_header = "Source"
    score_kind = ScoreKind.CONTINUOUS

    def score(self, expected_answer, given_answer):
        raise AssertionError("the scores of the source method must be reused")


def build_result():
    scores = (
        QuestionScore(Question("1", "Capital?", "Brasília"), "Brasília", 0.9, 1.0),
        QuestionScore(Question("2", "Autor?", "Machado de Assis"), "Machado", 0.4, 2.0),
        QuestionScore(Question("3", "Ano?", "1899"), "1900", 0.1, 3.0),
    )
    return EvaluationResult(scores, datetime(2026, 10, 28, 12, 0, 0), SourceScoringMethod())


def test_scores_every_question_with_every_method():
    overview = BuildMetricOverview().execute(build_result(), [ExactMatchScoringMethod(), TokenF1ScoringMethod()])

    assert [entry.method.identifier for entry in overview.entries] == ["exact_match", "token_f1"]
    assert overview.entries[0].scores == (1.0, 0.0, 0.0)
    assert overview.entries[1].scores == pytest.approx((1.0, 0.5, 0.0))


def test_keeps_the_questions_and_the_evaluation_date():
    result = build_result()

    overview = BuildMetricOverview().execute(result, [ExactMatchScoringMethod()])

    assert [question.identifier for question in overview.questions] == ["1", "2", "3"]
    assert overview.evaluated_at == result.evaluated_at


def test_reuses_the_scores_of_the_method_that_produced_the_result():
    overview = BuildMetricOverview().execute(build_result(), [SourceScoringMethod()])

    assert overview.entries[0].scores == (0.9, 0.4, 0.1)


def test_entries_summarize_their_scores():
    overview = BuildMetricOverview().execute(build_result(), [SourceScoringMethod()])

    assert overview.entries[0].average_score == pytest.approx(0.4666666667)
    assert overview.entries[0].median_score == pytest.approx(0.4)

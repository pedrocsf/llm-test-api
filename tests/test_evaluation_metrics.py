import pytest

from domain.entities.evaluation_metrics import EvaluationMetrics
from domain.entities.question import Question
from domain.entities.question_score import QuestionScore


def build_score(identifier, answer, score, response_seconds):
    return QuestionScore(Question(identifier, f"q{identifier}", "expected"), answer, score, response_seconds)


def test_summarizes_scores_and_response_time():
    scores = (
        build_score("1", "abcd", 0.9, 1.0),
        build_score("2", "ab", 0.3, 3.0),
        build_score("3", "", 0.0, 2.0),
    )

    metrics = EvaluationMetrics.from_scores(scores)

    assert metrics.question_count == 3
    assert metrics.average_score == pytest.approx(0.4)
    assert metrics.median_score == pytest.approx(0.3)
    assert metrics.highest.question.identifier == "1"
    assert metrics.lowest.question.identifier == "3"
    assert metrics.corpus_score is None
    assert metrics.average_response_seconds == pytest.approx(2.0)
    assert metrics.fastest_response_seconds == 1.0
    assert metrics.slowest_response_seconds == 3.0
    assert metrics.total_response_seconds == pytest.approx(6.0)
    assert metrics.empty_answer_count == 1
    assert metrics.average_answer_length == pytest.approx(2.0)


def test_counts_only_perfect_scores_as_correct():
    scores = (
        build_score("1", "a", 1.0, 0.1),
        build_score("2", "b", 0.99, 0.1),
        build_score("3", "c", 1.0, 0.1),
    )

    assert EvaluationMetrics.from_scores(scores).correct_count == 2


def test_carries_the_corpus_score():
    metrics = EvaluationMetrics.from_scores((build_score("1", "a", 0.5, 0.1),), corpus_score=0.42)

    assert metrics.corpus_score == 0.42


def test_blank_answers_count_as_empty():
    metrics = EvaluationMetrics.from_scores((build_score("1", "   ", 0.0, 0.1),))

    assert metrics.empty_answer_count == 1


def test_rejects_empty_scores():
    with pytest.raises(ValueError):
        EvaluationMetrics.from_scores(())

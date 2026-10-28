from dataclasses import dataclass
from statistics import fmean, median

from domain.entities.question_score import QuestionScore

PERFECT_SCORE = 1.0


@dataclass(frozen=True)
class EvaluationMetrics:
    question_count: int
    average_score: float
    median_score: float
    highest: QuestionScore
    lowest: QuestionScore
    correct_count: int
    corpus_score: float | None
    average_response_seconds: float
    fastest_response_seconds: float
    slowest_response_seconds: float
    total_response_seconds: float
    empty_answer_count: int
    average_answer_length: float

    @classmethod
    def from_scores(cls, scores: tuple[QuestionScore, ...], corpus_score: float | None = None) -> "EvaluationMetrics":
        if not scores:
            raise ValueError("Metrics require at least one score.")
        response_times = [score.response_seconds for score in scores]
        return cls(
            question_count=len(scores),
            average_score=fmean(score.score for score in scores),
            median_score=median(score.score for score in scores),
            highest=max(scores, key=lambda score: score.score),
            lowest=min(scores, key=lambda score: score.score),
            correct_count=sum(1 for score in scores if score.score >= PERFECT_SCORE),
            corpus_score=corpus_score,
            average_response_seconds=fmean(response_times),
            fastest_response_seconds=min(response_times),
            slowest_response_seconds=max(response_times),
            total_response_seconds=sum(response_times),
            empty_answer_count=sum(1 for score in scores if not score.given_answer.strip()),
            average_answer_length=fmean(len(score.given_answer) for score in scores),
        )

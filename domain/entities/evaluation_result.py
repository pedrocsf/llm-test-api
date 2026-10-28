from dataclasses import dataclass
from datetime import datetime

from domain.entities.evaluation_metrics import EvaluationMetrics
from domain.entities.question_score import QuestionScore
from domain.scoring.scoring_method import ScoringMethod


@dataclass(frozen=True)
class EvaluationResult:
    scores: tuple[QuestionScore, ...]
    evaluated_at: datetime
    method: ScoringMethod

    @property
    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(score.score for score in self.scores) / len(self.scores)

    @property
    def metrics(self) -> EvaluationMetrics:
        answer_pairs = [(score.question.expected_answer, score.given_answer) for score in self.scores]
        return EvaluationMetrics.from_scores(self.scores, self.method.corpus_score(answer_pairs))

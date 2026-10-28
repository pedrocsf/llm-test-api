from collections.abc import Sequence

from domain.entities.evaluation_result import EvaluationResult
from domain.entities.metric_overview import MetricOverview, MetricOverviewEntry
from domain.scoring.scoring_method import ScoringMethod


class BuildMetricOverview:
    def execute(self, result: EvaluationResult, methods: Sequence[ScoringMethod]) -> MetricOverview:
        entries = tuple(MetricOverviewEntry(method, self._scores_for(result, method)) for method in methods)
        questions = tuple(score.question for score in result.scores)
        return MetricOverview(questions, entries, result.evaluated_at)

    def _scores_for(self, result: EvaluationResult, method: ScoringMethod) -> tuple[float, ...]:
        if method.identifier == result.method.identifier:
            return tuple(score.score for score in result.scores)
        return tuple(method.score(score.question.expected_answer, score.given_answer) for score in result.scores)

from dataclasses import dataclass
from datetime import datetime
from statistics import fmean, median

from domain.entities.question import Question
from domain.scoring.scoring_method import ScoringMethod


@dataclass(frozen=True)
class MetricOverviewEntry:
    method: ScoringMethod
    scores: tuple[float, ...]

    @property
    def average_score(self) -> float:
        return fmean(self.scores)

    @property
    def median_score(self) -> float:
        return median(self.scores)


@dataclass(frozen=True)
class MetricOverview:
    questions: tuple[Question, ...]
    entries: tuple[MetricOverviewEntry, ...]
    evaluated_at: datetime

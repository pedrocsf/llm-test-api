from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum


class ScoreKind(Enum):
    CONTINUOUS = "continuous"
    BINARY = "binary"


class ScoringMethod(ABC):
    identifier: str
    display_name: str
    column_header: str
    score_kind: ScoreKind

    def prepare(self) -> None:
        return None

    @abstractmethod
    def score(self, expected_answer: str, given_answer: str) -> float:
        ...

    def corpus_score(self, answer_pairs: Sequence[tuple[str, str]]) -> float | None:
        return None

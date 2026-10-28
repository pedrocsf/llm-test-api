from collections.abc import Mapping, Sequence

from domain.scoring.scoring_method import ScoringMethod


class DemoScoringMethod(ScoringMethod):
    def __init__(
        self,
        reference: ScoringMethod,
        scores_by_answers: Mapping[tuple[str, str], float],
        corpus_value: float | None = None,
    ):
        self.identifier = reference.identifier
        self.display_name = reference.display_name
        self.column_header = reference.column_header
        self.score_kind = reference.score_kind
        self._scores_by_answers = scores_by_answers
        self._corpus_value = corpus_value

    def score(self, expected_answer: str, given_answer: str) -> float:
        return self._scores_by_answers[(expected_answer, given_answer)]

    def corpus_score(self, answer_pairs: Sequence[tuple[str, str]]) -> float | None:
        return self._corpus_value

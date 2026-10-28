from collections.abc import Sequence

from domain.scoring.scoring_method import ScoringMethod


class PrepareScoringMethods:
    def __init__(self, scoring_methods: Sequence[ScoringMethod]):
        self._scoring_methods = scoring_methods

    def execute(self) -> None:
        for scoring_method in self._scoring_methods:
            scoring_method.prepare()

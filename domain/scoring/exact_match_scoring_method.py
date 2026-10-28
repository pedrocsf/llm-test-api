from domain.scoring.scoring_method import ScoreKind, ScoringMethod
from domain.scoring.text_normalization import normalize_answer


class ExactMatchScoringMethod(ScoringMethod):
    identifier = "exact_match"
    display_name = "Exact match"
    column_header = "Exact match"
    score_kind = ScoreKind.BINARY

    def score(self, expected_answer: str, given_answer: str) -> float:
        return 1.0 if normalize_answer(expected_answer) == normalize_answer(given_answer) else 0.0

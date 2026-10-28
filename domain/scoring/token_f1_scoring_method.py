from collections import Counter

from domain.scoring.scoring_method import ScoreKind, ScoringMethod
from domain.scoring.text_normalization import normalized_tokens


class TokenF1ScoringMethod(ScoringMethod):
    identifier = "token_f1"
    display_name = "Token F1"
    column_header = "F1"
    score_kind = ScoreKind.CONTINUOUS

    def score(self, expected_answer: str, given_answer: str) -> float:
        expected_tokens = normalized_tokens(expected_answer)
        given_tokens = normalized_tokens(given_answer)
        if not expected_tokens or not given_tokens:
            return 1.0 if expected_tokens == given_tokens else 0.0
        shared_token_count = sum((Counter(expected_tokens) & Counter(given_tokens)).values())
        if shared_token_count == 0:
            return 0.0
        precision = shared_token_count / len(given_tokens)
        recall = shared_token_count / len(expected_tokens)
        return 2 * precision * recall / (precision + recall)

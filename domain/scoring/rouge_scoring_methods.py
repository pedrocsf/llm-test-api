from collections import Counter

from domain.scoring.scoring_method import ScoreKind, ScoringMethod
from domain.scoring.text_normalization import word_tokens


def _f_measure(overlap: int, candidate_size: int, reference_size: int) -> float:
    if overlap == 0:
        return 0.0
    precision = overlap / candidate_size
    recall = overlap / reference_size
    return 2 * precision * recall / (precision + recall)


def _ngram_counts(tokens: list[str], order: int) -> Counter:
    return Counter(tuple(tokens[start : start + order]) for start in range(len(tokens) - order + 1))


def _longest_common_subsequence_length(first: list[str], second: list[str]) -> int:
    previous_row = [0] * (len(second) + 1)
    for first_token in first:
        current_row = [0]
        for column, second_token in enumerate(second, start=1):
            if first_token == second_token:
                current_row.append(previous_row[column - 1] + 1)
            else:
                current_row.append(max(previous_row[column], current_row[column - 1]))
        previous_row = current_row
    return previous_row[-1]


class RougeNScoringMethod(ScoringMethod):
    score_kind = ScoreKind.CONTINUOUS

    def __init__(self, order: int):
        self._order = order
        self.identifier = f"rouge_{order}"
        self.display_name = f"ROUGE-{order}"
        self.column_header = f"ROUGE-{order}"

    def score(self, expected_answer: str, given_answer: str) -> float:
        reference_ngrams = _ngram_counts(word_tokens(expected_answer), self._order)
        candidate_ngrams = _ngram_counts(word_tokens(given_answer), self._order)
        overlap = sum((reference_ngrams & candidate_ngrams).values())
        return _f_measure(overlap, sum(candidate_ngrams.values()), sum(reference_ngrams.values()))


class RougeLScoringMethod(ScoringMethod):
    identifier = "rouge_l"
    display_name = "ROUGE-L"
    column_header = "ROUGE-L"
    score_kind = ScoreKind.CONTINUOUS

    def score(self, expected_answer: str, given_answer: str) -> float:
        reference_tokens = word_tokens(expected_answer)
        candidate_tokens = word_tokens(given_answer)
        overlap = _longest_common_subsequence_length(reference_tokens, candidate_tokens)
        return _f_measure(overlap, len(candidate_tokens), len(reference_tokens))

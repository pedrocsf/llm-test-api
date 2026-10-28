from collections.abc import Sequence

from sacrebleu import corpus_bleu, sentence_bleu

from domain.scoring.scoring_method import ScoreKind, ScoringMethod

SACREBLEU_SCALE = 100.0


class BleuScoringMethod(ScoringMethod):
    identifier = "bleu"
    display_name = "BLEU"
    column_header = "BLEU"
    score_kind = ScoreKind.CONTINUOUS

    def score(self, expected_answer: str, given_answer: str) -> float:
        return sentence_bleu(given_answer, [expected_answer]).score / SACREBLEU_SCALE

    def corpus_score(self, answer_pairs: Sequence[tuple[str, str]]) -> float | None:
        if not answer_pairs:
            return None
        references = [expected_answer for expected_answer, _ in answer_pairs]
        hypotheses = [given_answer for _, given_answer in answer_pairs]
        return corpus_bleu(hypotheses, [references]).score / SACREBLEU_SCALE

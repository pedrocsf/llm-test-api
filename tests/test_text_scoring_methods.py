import pytest

from domain.scoring.exact_match_scoring_method import ExactMatchScoringMethod
from domain.scoring.rouge_scoring_methods import RougeLScoringMethod, RougeNScoringMethod
from domain.scoring.scoring_method import ScoreKind
from domain.scoring.text_normalization import normalize_answer, normalized_tokens, word_tokens
from domain.scoring.token_f1_scoring_method import TokenF1ScoringMethod


def test_normalization_lowercases_and_drops_punctuation_articles_and_extra_spaces():
    assert normalize_answer("  The  Eiffel   Tower!! ") == "eiffel tower"


def test_normalization_drops_unicode_punctuation_but_keeps_accents():
    assert normalize_answer("Brasília… «capital»") == "brasília capital"


def test_word_tokens_keep_accented_letters():
    assert word_tokens("Não, é São Paulo") == ["não", "é", "são", "paulo"]


def test_normalized_tokens_split_on_whitespace():
    assert normalized_tokens("An apple a day") == ["apple", "day"]


def test_exact_match_ignores_case_punctuation_and_articles():
    method = ExactMatchScoringMethod()

    assert method.score("The Eiffel Tower", "eiffel tower.") == 1.0


def test_exact_match_rejects_any_other_difference():
    method = ExactMatchScoringMethod()

    assert method.score("Brasília", "A capital do Brasil é Brasília.") == 0.0


def test_exact_match_is_binary():
    assert ExactMatchScoringMethod().score_kind is ScoreKind.BINARY


def test_token_f1_balances_precision_and_recall():
    method = TokenF1ScoringMethod()

    assert method.score("cat sat down", "the cat sat") == pytest.approx(0.8)


def test_token_f1_counts_repeated_tokens_once_per_occurrence():
    method = TokenF1ScoringMethod()

    assert method.score("go go stop", "go stop stop") == pytest.approx(2 / 3)


def test_token_f1_is_zero_without_shared_tokens():
    assert TokenF1ScoringMethod().score("alpha beta", "gamma delta") == 0.0


def test_token_f1_is_zero_for_a_blank_answer():
    assert TokenF1ScoringMethod().score("alpha beta", "   ") == 0.0


def test_token_f1_is_one_when_both_sides_normalize_to_nothing():
    assert TokenF1ScoringMethod().score("the", "a") == 1.0


def test_rouge_1_scores_unigram_overlap():
    method = RougeNScoringMethod(1)

    assert method.score("the cat sat on the mat", "the cat on the mat") == pytest.approx(10 / 11)


def test_rouge_2_scores_bigram_overlap():
    method = RougeNScoringMethod(2)

    assert method.score("the cat sat on the mat", "the cat on the mat") == pytest.approx(2 / 3)


def test_rouge_l_scores_longest_common_subsequence():
    method = RougeLScoringMethod()

    assert method.score("the cat sat on the mat", "the cat on the mat") == pytest.approx(10 / 11)


def test_rouge_l_respects_word_order():
    method = RougeLScoringMethod()

    assert method.score("one two three", "three two one") == pytest.approx(1 / 3)


def test_rouge_is_zero_for_empty_or_unrelated_answers():
    assert RougeNScoringMethod(2).score("alpha beta", "alpha") == 0.0
    assert RougeLScoringMethod().score("alpha beta", "") == 0.0


def test_rouge_methods_expose_their_names():
    assert RougeNScoringMethod(2).identifier == "rouge_2"
    assert RougeNScoringMethod(2).column_header == "ROUGE-2"
    assert RougeLScoringMethod().column_header == "ROUGE-L"


def test_continuous_methods_have_no_corpus_score():
    assert TokenF1ScoringMethod().corpus_score([("a", "b")]) is None

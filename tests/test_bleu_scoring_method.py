import pytest

from data.scoring.bleu_scoring_method import BleuScoringMethod


def test_identical_sentences_score_one():
    method = BleuScoringMethod()

    assert method.score("the cat sat on the mat", "the cat sat on the mat") == pytest.approx(1.0)


def test_partial_overlap_scores_between_zero_and_one():
    method = BleuScoringMethod()

    score = method.score("o gato dorme no sofá", "o gato")

    assert 0.0 < score < 1.0


def test_blank_answer_scores_zero():
    assert BleuScoringMethod().score("o gato dorme", "") == 0.0


def test_corpus_score_is_computed_over_all_pairs():
    method = BleuScoringMethod()
    pairs = [("the cat sat", "the cat sat"), ("the dog barks loudly", "a dog barks loudly")]

    assert method.corpus_score(pairs) == pytest.approx(0.6914, abs=1e-3)


def test_corpus_score_is_absent_without_pairs():
    assert BleuScoringMethod().corpus_score([]) is None

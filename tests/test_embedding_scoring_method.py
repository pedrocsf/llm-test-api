import numpy as np
import pytest

from data.scoring.embedding_scoring_method import WARM_UP_TEXT, EmbeddingScoringMethod
from domain.errors import ModelUnavailableError


class FakeModel:
    def __init__(self, vectors):
        self._vectors = vectors

    def embed(self, texts):
        return [self._vectors[text] for text in texts]


def build_calculator(tmp_path, vectors):
    calculator = EmbeddingScoringMethod(tmp_path)
    calculator._model = FakeModel({text: np.array(vector) for text, vector in vectors.items()})
    return calculator


def test_prepare_loads_and_warms_up_the_model(tmp_path):
    calculator = build_calculator(tmp_path, {WARM_UP_TEXT: [1.0, 0.0]})

    calculator.prepare()


def test_prepare_reports_a_model_that_cannot_be_loaded(tmp_path, monkeypatch):
    def failing_model(**arguments):
        raise OSError("no cached model")

    monkeypatch.setattr("data.scoring.embedding_scoring_method.TextEmbedding", failing_model)

    with pytest.raises(ModelUnavailableError, match="no cached model"):
        EmbeddingScoringMethod(tmp_path).prepare()


def test_identical_direction_scores_one(tmp_path):
    calculator = build_calculator(tmp_path, {"a": [1.0, 0.0], "b": [2.0, 0.0]})

    assert calculator.score("a", "b") == pytest.approx(1.0)


def test_orthogonal_vectors_score_zero(tmp_path):
    calculator = build_calculator(tmp_path, {"a": [1.0, 0.0], "b": [0.0, 1.0]})

    assert calculator.score("a", "b") == pytest.approx(0.0)


def test_opposite_vectors_are_clamped_to_zero(tmp_path):
    calculator = build_calculator(tmp_path, {"a": [1.0, 0.0], "b": [-1.0, 0.0]})

    assert calculator.score("a", "b") == 0.0


def test_blank_answer_scores_zero_without_loading_model(tmp_path):
    calculator = EmbeddingScoringMethod(tmp_path)

    assert calculator.score("a", "   ") == 0.0

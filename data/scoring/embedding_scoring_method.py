from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

from domain.errors import ModelUnavailableError
from domain.scoring.scoring_method import ScoreKind, ScoringMethod

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
WARM_UP_TEXT = "warm-up"
MINIMUM_SIMILARITY = 0.0
MAXIMUM_SIMILARITY = 1.0


class EmbeddingScoringMethod(ScoringMethod):
    identifier = "embedding"
    display_name = "Embedding similarity"
    column_header = "Similarity"
    score_kind = ScoreKind.CONTINUOUS

    def __init__(self, models_directory: Path):
        self._models_directory = models_directory
        self._model: TextEmbedding | None = None

    def prepare(self) -> None:
        self._embed(WARM_UP_TEXT, WARM_UP_TEXT)

    def score(self, expected_answer: str, given_answer: str) -> float:
        if not given_answer.strip():
            return MINIMUM_SIMILARITY
        expected_vector, given_vector = self._embed(expected_answer, given_answer)
        return self._cosine_similarity(expected_vector, given_vector)

    def _embed(self, first_text: str, second_text: str) -> list[np.ndarray]:
        return [np.asarray(vector) for vector in self._load_model().embed([first_text, second_text])]

    def _load_model(self) -> TextEmbedding:
        if self._model is not None:
            return self._model
        try:
            self._model = TextEmbedding(
                model_name=EMBEDDING_MODEL_NAME,
                cache_dir=str(self._models_directory),
            )
        except Exception as error:
            raise ModelUnavailableError(f"Could not load the embedding model: {error}") from error
        return self._model

    def _cosine_similarity(self, first_vector: np.ndarray, second_vector: np.ndarray) -> float:
        norm_product = np.linalg.norm(first_vector) * np.linalg.norm(second_vector)
        if norm_product == 0:
            return MINIMUM_SIMILARITY
        cosine = float(np.dot(first_vector, second_vector) / norm_product)
        return min(max(cosine, MINIMUM_SIMILARITY), MAXIMUM_SIMILARITY)

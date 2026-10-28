import pytest

from domain.errors import ModelUnavailableError
from domain.scoring.scoring_method import ScoreKind, ScoringMethod
from domain.usecases.prepare_scoring_methods import PrepareScoringMethods


class FakeScoringMethod(ScoringMethod):
    identifier = "fake"
    display_name = "Fake"
    column_header = "Fake"
    score_kind = ScoreKind.CONTINUOUS

    def __init__(self, error=None):
        self.prepare_calls = 0
        self._error = error

    def prepare(self):
        self.prepare_calls += 1
        if self._error:
            raise self._error

    def score(self, expected_answer, given_answer):
        return 0.0


def test_prepares_every_method_once():
    methods = [FakeScoringMethod(), FakeScoringMethod()]

    PrepareScoringMethods(methods).execute()

    assert [method.prepare_calls for method in methods] == [1, 1]


def test_propagates_model_errors():
    methods = [FakeScoringMethod(ModelUnavailableError("missing"))]

    with pytest.raises(ModelUnavailableError):
        PrepareScoringMethods(methods).execute()

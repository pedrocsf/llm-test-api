from pathlib import Path

from domain.entities.question import Question
from domain.errors import QuestionsUnavailableError
from domain.repositories.question_repository import QuestionRepository
from domain.scoring.exact_match_scoring_method import ExactMatchScoringMethod
from domain.scoring.token_f1_scoring_method import TokenF1ScoringMethod
from domain.usecases.build_metric_overview import BuildMetricOverview
from domain.usecases.export_result import ExportResult
from domain.usecases.load_questions import LoadQuestions
from domain.usecases.rescore_result import RescoreResult
from domain.usecases.run_evaluation import RunEvaluation
from presentation.controllers.evaluation_controller import (
    MISSING_DATASET_MESSAGE,
    MISSING_ENDPOINT_MESSAGE,
    EvaluationController,
    EvaluationUseCases,
)


class FakeQuestionRepository(QuestionRepository):
    def __init__(self, questions=None, error=None):
        self._questions = questions or []
        self._error = error

    def load(self, source):
        if self._error:
            raise self._error
        return self._questions


def build_controller(repository):
    use_cases = EvaluationUseCases(
        load_questions=LoadQuestions(repository),
        run_evaluation=RunEvaluation(None),
        rescore_result=RescoreResult(),
        build_overview=BuildMetricOverview(),
        export_result=ExportResult(None),
    )
    return EvaluationController(use_cases, [TokenF1ScoringMethod(), ExactMatchScoringMethod()])


def record(signal):
    received = []
    signal.connect(lambda *arguments: received.append(arguments))
    return received


def test_starts_with_the_first_scoring_method_selected():
    controller = build_controller(FakeQuestionRepository())

    assert controller.selected_method.identifier == "token_f1"
    assert [method.identifier for method in controller.scoring_methods] == ["token_f1", "exact_match"]


def test_selecting_a_method_without_results_only_changes_the_selection():
    controller = build_controller(FakeQuestionRepository())
    started = record(controller.started)

    controller.select_method("exact_match")

    assert controller.selected_method.identifier == "exact_match"
    assert started == []


def test_ignores_an_unknown_method():
    controller = build_controller(FakeQuestionRepository())

    controller.select_method("does_not_exist")

    assert controller.selected_method.identifier == "token_f1"


def test_shutdown_without_a_running_task_does_nothing():
    controller = build_controller(FakeQuestionRepository())

    controller.shutdown()


def test_ignores_an_overview_request_without_a_result():
    controller = build_controller(FakeQuestionRepository())
    ready = record(controller.overview_ready)
    failed = record(controller.overview_failed)

    controller.build_overview()

    assert ready == []
    assert failed == []


def test_announces_a_loaded_dataset():
    controller = build_controller(FakeQuestionRepository([Question("1", "a?", "A"), Question("2", "b?", "B")]))
    loaded = record(controller.dataset_loaded)

    controller.load_dataset(Path("/data/questions.json"))

    assert loaded == [("/data/questions.json", 2)]


def test_reports_a_dataset_that_cannot_be_loaded():
    controller = build_controller(FakeQuestionRepository(error=QuestionsUnavailableError("broken file")))
    loaded = record(controller.dataset_loaded)
    failures = record(controller.dataset_failed)

    controller.load_dataset(Path("/data/questions.json"))

    assert loaded == []
    assert failures == [("broken file",)]


def test_refuses_to_run_without_a_dataset():
    controller = build_controller(FakeQuestionRepository())
    failures = record(controller.failed)
    started = record(controller.started)

    controller.start_evaluation("http://127.0.0.1:1234/v1/chat/completions", "", "")

    assert failures == [(MISSING_DATASET_MESSAGE,)]
    assert started == []


def test_refuses_to_run_without_an_endpoint():
    controller = build_controller(FakeQuestionRepository([Question("1", "a?", "A")]))
    controller.load_dataset(Path("/data/questions.json"))
    failures = record(controller.failed)

    controller.start_evaluation("   ", "", "")

    assert failures == [(MISSING_ENDPOINT_MESSAGE,)]

from pathlib import Path

import pytest

from data.scoring.bleu_scoring_method import BleuScoringMethod
from demo.demo_data import DEMO_CORPUS_BLEU_SCORE, DEMO_ENTRIES
from demo.demo_question_repository import DemoQuestionRepository
from demo.demo_run_evaluation import DemoRunEvaluation
from domain.entities.evaluation_request import EvaluationRequest
from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import EvaluationCancelledError
from domain.scoring.exact_match_scoring_method import ExactMatchScoringMethod
from domain.scoring.rouge_scoring_methods import RougeLScoringMethod, RougeNScoringMethod
from domain.scoring.scoring_method import ScoreKind
from domain.scoring.token_f1_scoring_method import TokenF1ScoringMethod
from domain.usecases.build_metric_overview import BuildMetricOverview
from domain.usecases.load_questions import LoadQuestions
from domain.usecases.rescore_result import RescoreResult
from main_demo import build_demo_methods

SETTINGS = LanguageModelSettings(endpoint_url="http://127.0.0.1:1234/v1/chat/completions")
SCORE_TOLERANCE = 1e-3


def build_request(method):
    questions = tuple(LoadQuestions(DemoQuestionRepository(DEMO_ENTRIES)).execute(Path("demo-dataset.json")))
    return EvaluationRequest(SETTINGS, questions, method)


def lexical_methods():
    return [
        ExactMatchScoringMethod(),
        TokenF1ScoringMethod(),
        RougeNScoringMethod(1),
        RougeNScoringMethod(2),
        RougeLScoringMethod(),
        BleuScoringMethod(),
    ]


def test_every_entry_scores_every_available_method():
    from main import build_scoring_methods

    identifiers = {method.identifier for method in build_scoring_methods()}

    assert all(set(entry.scores) == identifiers for entry in DEMO_ENTRIES)


@pytest.mark.parametrize("method", lexical_methods(), ids=lambda method: method.identifier)
def test_fixed_scores_match_the_real_formulas(method):
    for entry in DEMO_ENTRIES:
        real_score = method.score(entry.expected_answer, entry.given_answer)

        assert entry.scores[method.identifier] == pytest.approx(real_score, abs=SCORE_TOLERANCE), entry.identifier


def test_fixed_corpus_bleu_matches_the_real_formula():
    pairs = [(entry.expected_answer, entry.given_answer) for entry in DEMO_ENTRIES]

    assert DEMO_CORPUS_BLEU_SCORE == pytest.approx(BleuScoringMethod().corpus_score(pairs), abs=SCORE_TOLERANCE)


def test_every_fixed_score_is_between_zero_and_one():
    assert all(0.0 <= value <= 1.0 for entry in DEMO_ENTRIES for value in entry.scores.values())


def test_demo_methods_mirror_the_real_ones():
    from main import build_scoring_methods

    real = [(m.identifier, m.display_name, m.column_header, m.score_kind) for m in build_scoring_methods()]
    demo = [(m.identifier, m.display_name, m.column_header, m.score_kind) for m in build_demo_methods()]

    assert demo == real


def test_demo_methods_return_the_fixed_scores():
    exact_match = next(method for method in build_demo_methods() if method.identifier == "exact_match")
    entry = DEMO_ENTRIES[0]

    assert exact_match.score(entry.expected_answer, entry.given_answer) == 1.0
    assert exact_match.score_kind is ScoreKind.BINARY


def test_only_bleu_reports_a_corpus_score():
    corpus_values = {method.identifier: method.corpus_score([]) for method in build_demo_methods()}

    assert corpus_values.pop("bleu") == DEMO_CORPUS_BLEU_SCORE
    assert all(value is None for value in corpus_values.values())


def test_the_demo_dataset_has_twelve_questions():
    questions = DemoQuestionRepository(DEMO_ENTRIES).load(Path("anything.json"))

    assert len(questions) == 12
    assert questions[0].text == DEMO_ENTRIES[0].question


def test_the_simulated_run_uses_the_fixed_answers_and_times():
    method = build_demo_methods()[0]

    result = DemoRunEvaluation(DEMO_ENTRIES, step_seconds=0).execute(build_request(method))

    assert [score.given_answer for score in result.scores] == [entry.given_answer for entry in DEMO_ENTRIES]
    assert [score.response_seconds for score in result.scores] == [entry.response_seconds for entry in DEMO_ENTRIES]
    assert [score.score for score in result.scores] == [entry.scores["embedding"] for entry in DEMO_ENTRIES]


def test_the_simulated_run_reports_progress():
    progress = []

    DemoRunEvaluation(DEMO_ENTRIES, step_seconds=0).execute(
        build_request(build_demo_methods()[0]), on_progress=lambda completed, total: progress.append((completed, total))
    )

    assert progress[0] == (1, 12)
    assert progress[-1] == (12, 12)


def test_the_simulated_run_can_be_cancelled():
    with pytest.raises(EvaluationCancelledError):
        DemoRunEvaluation(DEMO_ENTRIES, step_seconds=0).execute(
            build_request(build_demo_methods()[0]), is_cancelled=lambda: True
        )


def test_switching_metrics_and_building_the_overview_work_with_the_demo_methods():
    methods = build_demo_methods()
    result = DemoRunEvaluation(DEMO_ENTRIES, step_seconds=0).execute(build_request(methods[0]))

    rescored = RescoreResult().execute(result, methods[1])
    overview = BuildMetricOverview().execute(result, methods)

    assert [score.score for score in rescored.scores] == [entry.scores["exact_match"] for entry in DEMO_ENTRIES]
    assert [entry.method.identifier for entry in overview.entries] == [method.identifier for method in methods]
    assert rescored.metrics.correct_count == 3

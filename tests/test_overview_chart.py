import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime

import pytest
from PySide6.QtGui import QGuiApplication

from domain.entities.metric_overview import MetricOverview, MetricOverviewEntry
from domain.entities.question import Question
from domain.scoring.exact_match_scoring_method import ExactMatchScoringMethod
from domain.scoring.rouge_scoring_methods import RougeLScoringMethod
from domain.scoring.token_f1_scoring_method import TokenF1ScoringMethod
from presentation.views.overview_chart import (
    MAX_HEATMAP_WIDTH,
    MIN_TICK_SPACING,
    PIXEL_RATIO,
    render_overview_chart,
    tick_step_for,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@pytest.fixture(scope="module")
def application():
    return QGuiApplication.instance() or QGuiApplication([])


def build_overview(question_count, methods=None):
    methods = methods or [ExactMatchScoringMethod(), TokenF1ScoringMethod(), RougeLScoringMethod()]
    questions = tuple(
        Question(str(number), f"Question number {number}?", "answer") for number in range(1, question_count + 1)
    )
    entries = tuple(
        MetricOverviewEntry(method, tuple((number % 5) / 4 for number in range(question_count))) for method in methods
    )
    return MetricOverview(questions, entries, datetime(2026, 10, 28, 12, 0, 0))


def test_renders_a_non_empty_image(application):
    image = render_overview_chart(build_overview(3))

    assert not image.isNull()
    assert image.width() > 0 and image.height() > 0


def test_height_depends_on_the_metrics_and_not_on_the_questions(application):
    few_questions = render_overview_chart(build_overview(3))
    many_questions = render_overview_chart(build_overview(1000))

    assert few_questions.height() == many_questions.height()


def test_more_metrics_make_the_image_taller(application):
    three_metrics = render_overview_chart(build_overview(5))
    one_metric = render_overview_chart(build_overview(5, [TokenF1ScoringMethod()]))

    assert three_metrics.height() > one_metric.height()


def test_more_questions_make_the_image_wider(application):
    few_questions = render_overview_chart(build_overview(5))
    many_questions = render_overview_chart(build_overview(60))

    assert many_questions.width() > few_questions.width()


def test_width_stops_growing_at_the_heatmap_limit(application):
    large = render_overview_chart(build_overview(1000))
    larger = render_overview_chart(build_overview(5000))

    assert large.width() == larger.width()
    assert large.width() < (MAX_HEATMAP_WIDTH + 1200) * PIXEL_RATIO


def test_renders_with_a_single_metric_and_a_single_question(application):
    image = render_overview_chart(build_overview(1, [TokenF1ScoringMethod()]))

    assert not image.isNull()


def test_saves_a_valid_png_file(application, tmp_path):
    destination = tmp_path / "overview.png"

    assert render_overview_chart(build_overview(5)).save(str(destination))

    assert destination.read_bytes().startswith(PNG_SIGNATURE)


def test_labels_every_question_when_cells_are_wide():
    assert tick_step_for(cell_width=80) == 1


def test_skips_question_numbers_when_cells_are_narrow():
    assert tick_step_for(cell_width=2) == 50
    assert tick_step_for(cell_width=24) == 5


def test_tick_labels_never_get_closer_than_the_minimum_spacing():
    for cell_width in (0.5, 1, 2.4, 7, 13, 33, 48, 120):
        assert tick_step_for(cell_width) * cell_width >= MIN_TICK_SPACING

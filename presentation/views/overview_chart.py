from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPen

from domain.entities.metric_overview import MetricOverview, MetricOverviewEntry
from domain.scoring.scoring_method import ScoreKind
from presentation.views.branding import (
    ACCENT_BLUE,
    APPLICATION_NAME,
    APPLICATION_SUBTITLE,
    GRADIENT_END,
    GRADIENT_START,
    SOFT_BLUE,
)
from presentation.views.logo_mark import draw_logo

PIXEL_RATIO = 2
MARGIN = 56
HEADER_HEIGHT = 140
FOOTER_HEIGHT = 70
LOGO_SIZE = 72
PANEL_PADDING = 28
PANEL_RADIUS = 18
PANEL_TITLE_HEIGHT = 64
COLUMN_BAND_HEIGHT = 44
ROW_SLOT_HEIGHT = 64
ROW_GAP = 10
AXIS_HEIGHT = 48
LABEL_COLUMN_WIDTH = 200
BAR_COLUMN_WIDTH = 470
VALUE_LABEL_WIDTH = 76
COLUMN_GAP = 48
MIN_HEATMAP_WIDTH = 760
MAX_HEATMAP_WIDTH = 2000
PREFERRED_CELL_WIDTH = 48
MIN_VALUE_CELL_WIDTH = 44
MIN_GAP_CELL_WIDTH = 8
CELL_GAP = 3
CELL_RADIUS = 4
MIN_TICK_SPACING = 56
TICK_LENGTH = 6
BAR_THICKNESS = 24
BAR_RADIUS = 6
MEDIAN_MARKER_DIAMETER = 12
SCALE_BAR_WIDTH = 170
SCALE_BAR_HEIGHT = 10
GRID_VALUES = (0.0, 0.25, 0.5, 0.75, 1.0)
TICK_STEP_BASES = (1, 2, 5)
COLOR_SCALE_STOPS = (
    (0.0, "#440154"),
    (0.25, "#3b528b"),
    (0.5, "#21918c"),
    (0.75, "#5ec962"),
    (1.0, "#fde725"),
)
DARK_TEXT_COLOR = QColor(GRADIENT_START)
LIGHT_TEXT_COLOR = QColor(255, 255, 255)
SOFT_TEXT_COLOR = QColor(SOFT_BLUE)
PANEL_FILL_COLOR = QColor(255, 255, 255, 18)
PANEL_BORDER_COLOR = QColor(255, 255, 255, 36)
GRID_LINE_COLOR = QColor(255, 255, 255, 40)
LIGHT_CELL_LIGHTNESS = 140


@dataclass(frozen=True)
class _Geometry:
    canvas_width: float
    canvas_height: float
    panel: QRectF
    label_left: float
    bar_left: float
    bar_right: float
    heatmap_left: float
    cell_width: float
    plot_top: float
    plot_bottom: float


def tick_step_for(cell_width: float) -> int:
    magnitude = 1
    while True:
        for base in TICK_STEP_BASES:
            step = base * magnitude
            if step * cell_width >= MIN_TICK_SPACING:
                return step
        magnitude *= 10


def render_overview_chart(overview: MetricOverview) -> QImage:
    geometry = _build_geometry(len(overview.questions), len(overview.entries))
    image = QImage(
        int(geometry.canvas_width * PIXEL_RATIO),
        int(geometry.canvas_height * PIXEL_RATIO),
        QImage.Format.Format_ARGB32,
    )
    image.setDevicePixelRatio(PIXEL_RATIO)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    _draw_background(painter, geometry)
    _draw_header(painter, overview)
    _draw_panel(painter, geometry.panel)
    _draw_panel_titles(painter, geometry)
    _draw_bar_grid(painter, geometry)
    for index, entry in enumerate(overview.entries):
        center_y = geometry.plot_top + ROW_SLOT_HEIGHT * (index + 0.5)
        _draw_metric_label(painter, entry, center_y, geometry)
        _draw_bar(painter, entry, center_y, geometry)
        _draw_heatmap_strip(painter, entry, center_y, geometry)
    _draw_question_axis(painter, len(overview.questions), geometry)
    _draw_footer(painter, geometry, overview)
    painter.end()
    return image


def _build_geometry(question_count: int, metric_count: int) -> _Geometry:
    questions = max(1, question_count)
    rows = max(1, metric_count)
    heatmap_width = min(MAX_HEATMAP_WIDTH, max(MIN_HEATMAP_WIDTH, questions * PREFERRED_CELL_WIDTH))
    inner_width = LABEL_COLUMN_WIDTH + BAR_COLUMN_WIDTH + COLUMN_GAP + heatmap_width
    panel_height = 2 * PANEL_PADDING + PANEL_TITLE_HEIGHT + COLUMN_BAND_HEIGHT + rows * ROW_SLOT_HEIGHT + AXIS_HEIGHT
    label_left = MARGIN + PANEL_PADDING
    plot_top = HEADER_HEIGHT + PANEL_PADDING + PANEL_TITLE_HEIGHT + COLUMN_BAND_HEIGHT
    return _Geometry(
        canvas_width=2 * MARGIN + 2 * PANEL_PADDING + inner_width,
        canvas_height=HEADER_HEIGHT + panel_height + FOOTER_HEIGHT,
        panel=QRectF(MARGIN, HEADER_HEIGHT, 2 * PANEL_PADDING + inner_width, panel_height),
        label_left=label_left,
        bar_left=label_left + LABEL_COLUMN_WIDTH,
        bar_right=label_left + LABEL_COLUMN_WIDTH + BAR_COLUMN_WIDTH - VALUE_LABEL_WIDTH,
        heatmap_left=label_left + LABEL_COLUMN_WIDTH + BAR_COLUMN_WIDTH + COLUMN_GAP,
        cell_width=heatmap_width / questions,
        plot_top=plot_top,
        plot_bottom=plot_top + rows * ROW_SLOT_HEIGHT,
    )


def _set_font(painter: QPainter, pixel_size: int, bold: bool = False) -> None:
    font = QFont(painter.font())
    font.setPixelSize(pixel_size)
    font.setBold(bold)
    painter.setFont(font)


def _draw_background(painter: QPainter, geometry: _Geometry) -> None:
    gradient = QLinearGradient(0, 0, geometry.canvas_width, geometry.canvas_height)
    gradient.setColorAt(0.0, QColor(GRADIENT_START))
    gradient.setColorAt(1.0, QColor(GRADIENT_END))
    painter.fillRect(QRectF(0, 0, geometry.canvas_width, geometry.canvas_height), gradient)


def _draw_header(painter: QPainter, overview: MetricOverview) -> None:
    painter.save()
    painter.translate(MARGIN, 36)
    draw_logo(painter, LOGO_SIZE)
    painter.restore()
    text_left = MARGIN + LOGO_SIZE + 24
    painter.setPen(LIGHT_TEXT_COLOR)
    _set_font(painter, 36, bold=True)
    painter.drawText(QPointF(text_left, 74), APPLICATION_NAME)
    painter.setPen(SOFT_TEXT_COLOR)
    _set_font(painter, 20)
    subtitle = f"Metric overview · {len(overview.questions)} questions · {overview.evaluated_at:%Y-%m-%d %H:%M}"
    painter.drawText(QPointF(text_left, 104), subtitle)


def _draw_panel(painter: QPainter, rect: QRectF) -> None:
    painter.setPen(QPen(PANEL_BORDER_COLOR, 1))
    painter.setBrush(PANEL_FILL_COLOR)
    painter.drawRoundedRect(rect, PANEL_RADIUS, PANEL_RADIUS)


def _draw_panel_titles(painter: QPainter, geometry: _Geometry) -> None:
    inner = geometry.panel.adjusted(PANEL_PADDING, PANEL_PADDING, -PANEL_PADDING, -PANEL_PADDING)
    painter.setPen(LIGHT_TEXT_COLOR)
    _set_font(painter, 24, bold=True)
    painter.drawText(QPointF(inner.left(), inner.top() + 24), "Performance per metric")
    painter.setPen(SOFT_TEXT_COLOR)
    _set_font(painter, 15)
    painter.drawText(
        QPointF(inner.left(), inner.top() + 50),
        "Bar: mean  ·  Dot: median  ·  Strip: score of each question, in dataset order",
    )
    _draw_color_scale(
        painter, QRectF(inner.right() - SCALE_BAR_WIDTH, inner.top() + 6, SCALE_BAR_WIDTH, SCALE_BAR_HEIGHT)
    )
    band_baseline = geometry.plot_top - 14
    painter.setPen(LIGHT_TEXT_COLOR)
    _set_font(painter, 17, bold=True)
    painter.drawText(QPointF(geometry.bar_left, band_baseline), "Average score")
    painter.drawText(QPointF(geometry.heatmap_left, band_baseline), "Score per question (x: question number)")


def _draw_color_scale(painter: QPainter, rect: QRectF) -> None:
    gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
    for stop, color in COLOR_SCALE_STOPS:
        gradient.setColorAt(stop, QColor(color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawRoundedRect(rect, SCALE_BAR_HEIGHT / 2, SCALE_BAR_HEIGHT / 2)
    painter.setPen(SOFT_TEXT_COLOR)
    _set_font(painter, 13)
    painter.drawText(QPointF(rect.left(), rect.bottom() + 18), "0")
    painter.drawText(QPointF(rect.right() - 8, rect.bottom() + 18), "1")


def _draw_bar_grid(painter: QPainter, geometry: _Geometry) -> None:
    _set_font(painter, 14)
    axis_width = geometry.bar_right - geometry.bar_left
    for value in GRID_VALUES:
        x = geometry.bar_left + value * axis_width
        painter.setPen(QPen(GRID_LINE_COLOR, 1))
        painter.drawLine(QPointF(x, geometry.plot_top), QPointF(x, geometry.plot_bottom))
        painter.setPen(SOFT_TEXT_COLOR)
        label_rect = QRectF(x - 30, geometry.plot_bottom + 6, 60, AXIS_HEIGHT - 6)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, f"{value:g}")


def _draw_metric_label(painter: QPainter, entry: MetricOverviewEntry, center_y: float, geometry: _Geometry) -> None:
    painter.setPen(LIGHT_TEXT_COLOR)
    _set_font(painter, 17)
    label = painter.fontMetrics().elidedText(
        entry.method.display_name, Qt.TextElideMode.ElideRight, int(LABEL_COLUMN_WIDTH - 20)
    )
    label_rect = QRectF(geometry.label_left, center_y - 16, LABEL_COLUMN_WIDTH - 16, 32)
    painter.drawText(label_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)


def _draw_bar(painter: QPainter, entry: MetricOverviewEntry, center_y: float, geometry: _Geometry) -> None:
    axis_width = geometry.bar_right - geometry.bar_left
    gradient = QLinearGradient(geometry.bar_left, 0, geometry.bar_right, 0)
    gradient.setColorAt(0.0, QColor(ACCENT_BLUE))
    gradient.setColorAt(1.0, QColor(SOFT_BLUE))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    bar_width = max(2.0, entry.average_score * axis_width)
    painter.drawRoundedRect(
        QRectF(geometry.bar_left, center_y - BAR_THICKNESS / 2, bar_width, BAR_THICKNESS), BAR_RADIUS, BAR_RADIUS
    )

    median_x = geometry.bar_left + entry.median_score * axis_width
    painter.setPen(QPen(DARK_TEXT_COLOR, 2))
    painter.setBrush(LIGHT_TEXT_COLOR)
    painter.drawEllipse(QPointF(median_x, center_y), MEDIAN_MARKER_DIAMETER / 2, MEDIAN_MARKER_DIAMETER / 2)

    painter.setPen(LIGHT_TEXT_COLOR)
    _set_font(painter, 18, bold=True)
    value_rect = QRectF(geometry.bar_right + 12, center_y - 16, VALUE_LABEL_WIDTH, 32)
    painter.drawText(
        value_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"{entry.average_score:.3f}"
    )


def _draw_heatmap_strip(painter: QPainter, entry: MetricOverviewEntry, center_y: float, geometry: _Geometry) -> None:
    strip_height = ROW_SLOT_HEIGHT - ROW_GAP
    top = center_y - strip_height / 2
    cell_width = geometry.cell_width
    is_dense = cell_width < MIN_GAP_CELL_WIDTH
    show_values = cell_width >= MIN_VALUE_CELL_WIDTH
    value_format = "{:.0f}" if entry.method.score_kind is ScoreKind.BINARY else "{:.2f}"

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, not is_dense)
    for column, score in enumerate(entry.scores):
        left = geometry.heatmap_left + column * cell_width
        color = _color_for_score(score)
        if is_dense:
            right = geometry.heatmap_left + (column + 1) * cell_width
            painter.fillRect(QRectF(round(left), top, round(right) - round(left), strip_height), color)
            continue
        cell = QRectF(left + CELL_GAP / 2, top, cell_width - CELL_GAP, strip_height)
        painter.setBrush(color)
        painter.drawRoundedRect(cell, CELL_RADIUS, CELL_RADIUS)
        if show_values:
            _draw_cell_value(painter, cell, color, value_format.format(score))
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)


def _draw_cell_value(painter: QPainter, cell: QRectF, background: QColor, text: str) -> None:
    painter.setPen(DARK_TEXT_COLOR if background.lightness() > LIGHT_CELL_LIGHTNESS else LIGHT_TEXT_COLOR)
    _set_font(painter, 15, bold=True)
    painter.drawText(cell, Qt.AlignmentFlag.AlignCenter, text)
    painter.setPen(Qt.PenStyle.NoPen)


def _draw_question_axis(painter: QPainter, question_count: int, geometry: _Geometry) -> None:
    step = tick_step_for(geometry.cell_width)
    painter.setPen(QPen(SOFT_TEXT_COLOR, 1))
    _set_font(painter, 14)
    for number in _tick_numbers(question_count, step, geometry.cell_width):
        x = geometry.heatmap_left + (number - 0.5) * geometry.cell_width
        painter.setPen(QPen(SOFT_TEXT_COLOR, 1))
        painter.drawLine(QPointF(x, geometry.plot_bottom + 2), QPointF(x, geometry.plot_bottom + 2 + TICK_LENGTH))
        label_rect = QRectF(x - 30, geometry.plot_bottom + 10, 60, AXIS_HEIGHT - 10)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, str(number))


def _tick_numbers(question_count: int, step: int, cell_width: float) -> list[int]:
    if step == 1:
        return list(range(1, question_count + 1))
    numbers = [1]
    numbers.extend(
        number for number in range(step, question_count + 1, step) if (number - 1) * cell_width >= MIN_TICK_SPACING
    )
    return numbers


def _color_for_score(score: float) -> QColor:
    clamped = min(max(score, 0.0), 1.0)
    for (low_stop, low_color), (high_stop, high_color) in zip(COLOR_SCALE_STOPS, COLOR_SCALE_STOPS[1:]):
        if clamped <= high_stop:
            ratio = (clamped - low_stop) / (high_stop - low_stop)
            return _blend(QColor(low_color), QColor(high_color), ratio)
    return QColor(COLOR_SCALE_STOPS[-1][1])


def _blend(first: QColor, second: QColor, ratio: float) -> QColor:
    return QColor(
        round(first.red() + (second.red() - first.red()) * ratio),
        round(first.green() + (second.green() - first.green()) * ratio),
        round(first.blue() + (second.blue() - first.blue()) * ratio),
    )


def _draw_footer(painter: QPainter, geometry: _Geometry, overview: MetricOverview) -> None:
    baseline = geometry.canvas_height - 28
    painter.setPen(SOFT_TEXT_COLOR)
    _set_font(painter, 15)
    painter.drawText(QPointF(MARGIN, baseline), f"{APPLICATION_NAME} · {APPLICATION_SUBTITLE}")
    notes = "Scores range from 0 to 1."
    if any(entry.method.score_kind is ScoreKind.BINARY for entry in overview.entries):
        notes += " Binary metrics score each answer 0 or 1."
    notes_rect = QRectF(MARGIN, baseline - 20, geometry.canvas_width - 2 * MARGIN, 28)
    painter.drawText(notes_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, notes)

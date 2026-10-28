from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from domain.entities.evaluation_result import EvaluationResult
from domain.entities.metric_overview import MetricOverview
from domain.scoring.scoring_method import ScoreKind
from presentation.controllers.evaluation_controller import EvaluationController
from presentation.views.branding import APPLICATION_NAME, APPLICATION_SUBTITLE
from presentation.views.logo_mark import LogoMark
from presentation.views.metrics_panel import MetricsPanel
from presentation.views.overview_chart import render_overview_chart
from presentation.views.theme import MAIN_WINDOW_STYLE
from presentation.views.themed_combo_box import ThemedComboBox

WINDOW_TITLE = "Project Harbor Benchmark - v1.0"
DEMO_TITLE_SUFFIX = " (Demo)"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 820
HEADER_LOGO_SIZE = 48
LAYOUT_MARGIN = 24
LAYOUT_SPACING = 14
ENDPOINT_PLACEHOLDER = "http://127.0.0.1:1234/v1/chat/completions"
OPTIONAL_API_KEY_PLACEHOLDER = "Optional"
OPTIONAL_MODEL_PLACEHOLDER = "Optional"
NO_DATASET_TEXT = "No dataset loaded"
FIXED_TABLE_HEADERS = ("Question", "Expected answer", "LLM answer")
SCORE_COLUMN = len(FIXED_TABLE_HEADERS)
CONTINUOUS_SCORE_FORMAT = "{:.3f}"
BINARY_SCORE_FORMAT = "{:.0f}"
PERCENTAGE_FORMAT = "{:.1%}"
DATASET_FILTERS = "JSON files (*.json);;All files (*)"
EXPORT_FILTERS = {"JSON (*.json)": ".json", "CSV (*.csv)": ".csv"}
DEFAULT_EXPORT_NAME = "result.json"
CHART_FILTER = "PNG image (*.png)"
CHART_SUFFIX = ".png"
DEFAULT_CHART_NAME = "overview.png"


@dataclass(frozen=True)
class MainWindowOptions:
    dataset_picker: Callable[[], Path | None] | None = None
    initial_endpoint: str = ""
    badge_text: str | None = None


class MainWindow(QMainWindow):
    def __init__(self, controller: EvaluationController, options: MainWindowOptions | None = None):
        super().__init__()
        self._controller = controller
        self._options = options or MainWindowOptions()
        self._pick_dataset = self._options.dataset_picker or self._pick_dataset_with_dialog
        self._last_directory = Path.home()
        self._pending_chart_destination: Path | None = None
        self._build_interface()
        self._connect_controller()
        self._show_awaiting_dataset_state()

    def _build_interface(self) -> None:
        self.setWindowTitle(WINDOW_TITLE + (DEMO_TITLE_SUFFIX if self._options.badge_text else ""))
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        layout = QVBoxLayout()
        layout.setContentsMargins(LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN)
        layout.setSpacing(LAYOUT_SPACING)
        layout.addLayout(self._build_header())
        layout.addLayout(self._build_connection_form())
        layout.addLayout(self._build_action_row())
        layout.addWidget(self._build_progress_area())
        layout.addWidget(self._build_results_table(), stretch=1)
        self._metrics_panel = MetricsPanel()
        layout.addWidget(self._metrics_panel)
        layout.addWidget(self._build_average_label())
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _build_header(self) -> QHBoxLayout:
        title_label = QLabel(APPLICATION_NAME)
        title_label.setObjectName("brandTitle")
        subtitle_label = QLabel(APPLICATION_SUBTITLE)
        subtitle_label.setObjectName("brandSubtitle")
        titles = QVBoxLayout()
        titles.setSpacing(0)
        titles.addWidget(title_label)
        titles.addWidget(subtitle_label)
        header = QHBoxLayout()
        header.setSpacing(14)
        header.addWidget(LogoMark(HEADER_LOGO_SIZE))
        header.addLayout(titles)
        header.addStretch(1)
        if self._options.badge_text:
            badge = QLabel(self._options.badge_text)
            badge.setObjectName("demoBadge")
            header.addWidget(badge, alignment=Qt.AlignmentFlag.AlignVCenter)
        return header

    def _build_connection_form(self) -> QFormLayout:
        self._endpoint_input = QLineEdit(self._options.initial_endpoint)
        self._endpoint_input.setPlaceholderText(ENDPOINT_PLACEHOLDER)
        self._api_key_input = QLineEdit()
        self._api_key_input.setPlaceholderText(OPTIONAL_API_KEY_PLACEHOLDER)
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._model_input = QLineEdit()
        self._model_input.setPlaceholderText(OPTIONAL_MODEL_PLACEHOLDER)
        self._method_combo = self._build_method_combo()
        form = QFormLayout()
        form.addRow("URL", self._endpoint_input)
        form.addRow("API key", self._api_key_input)
        form.addRow("Model", self._model_input)
        form.addRow("Metric", self._method_combo)
        return form

    def _build_method_combo(self) -> QComboBox:
        combo = ThemedComboBox()
        for method in self._controller.scoring_methods:
            combo.addItem(method.display_name, method.identifier)
        combo.setCurrentIndex(combo.findData(self._controller.selected_method.identifier))
        combo.currentIndexChanged.connect(self._on_method_changed)
        return combo

    def _build_action_row(self) -> QHBoxLayout:
        self._load_button = QPushButton("Load dataset…")
        self._run_button = QPushButton("Run")
        self._cancel_button = QPushButton("Cancel")
        self._export_button = QPushButton("Export…")
        self._chart_button = QPushButton("Export chart…")
        self._run_button.setObjectName("primaryButton")
        self._dataset_label = QLabel()
        self._dataset_label.setObjectName("datasetLabel")
        self._load_button.clicked.connect(self._on_load_clicked)
        self._run_button.clicked.connect(self._on_run_clicked)
        self._cancel_button.clicked.connect(self._controller.cancel_evaluation)
        self._export_button.clicked.connect(self._on_export_clicked)
        self._chart_button.clicked.connect(self._on_export_chart_clicked)
        row = QHBoxLayout()
        row.addWidget(self._load_button)
        row.addWidget(self._run_button)
        row.addWidget(self._cancel_button)
        row.addSpacing(12)
        row.addWidget(self._dataset_label)
        row.addStretch(1)
        row.addWidget(self._chart_button)
        row.addWidget(self._export_button)
        return row

    def _build_progress_area(self) -> QWidget:
        self._progress_bar = QProgressBar()
        self._progress_bar.setTextVisible(False)
        self._status_label = QLabel()
        self._status_label.setObjectName("statusLabel")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._progress_bar)
        layout.addWidget(self._status_label)
        container = QWidget()
        container.setLayout(layout)
        return container

    def _build_results_table(self) -> QTableWidget:
        self._table = QTableWidget(0, len(FIXED_TABLE_HEADERS) + 1)
        self._set_score_header(self._controller.selected_method.column_header)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setWordWrap(True)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(SCORE_COLUMN, QHeaderView.ResizeMode.ResizeToContents)
        return self._table

    def _build_average_label(self) -> QLabel:
        self._average_label = QLabel()
        self._average_label.setObjectName("averageLabel")
        font = self._average_label.font()
        font.setPointSize(font.pointSize() + 4)
        font.setBold(True)
        self._average_label.setFont(font)
        self._average_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        return self._average_label

    def _connect_controller(self) -> None:
        self._controller.dataset_loaded.connect(self._show_dataset_loaded)
        self._controller.dataset_failed.connect(self._show_dataset_failure)
        self._controller.started.connect(self._show_running_state)
        self._controller.progressed.connect(self._show_progress)
        self._controller.completed.connect(self._show_result)
        self._controller.failed.connect(self._show_failure)
        self._controller.cancelled.connect(self._show_cancelled)
        self._controller.exported.connect(self._show_export_success)
        self._controller.export_failed.connect(self._show_export_failure)
        self._controller.overview_ready.connect(self._save_overview_chart)
        self._controller.overview_failed.connect(self._show_overview_failure)

    def _on_load_clicked(self) -> None:
        selected_source = self._pick_dataset()
        if selected_source is not None:
            self._controller.load_dataset(selected_source)

    def _pick_dataset_with_dialog(self) -> Path | None:
        selected_path, _ = QFileDialog.getOpenFileName(
            self, "Load dataset", str(self._last_directory), DATASET_FILTERS
        )
        if not selected_path:
            return None
        self._last_directory = Path(selected_path).parent
        return Path(selected_path)

    def _on_run_clicked(self) -> None:
        self._controller.start_evaluation(
            self._endpoint_input.text(),
            self._api_key_input.text(),
            self._model_input.text(),
        )

    def _on_method_changed(self, index: int) -> None:
        self._controller.select_method(self._method_combo.itemData(index))
        self._set_score_header(self._controller.selected_method.column_header)

    def _on_export_clicked(self) -> None:
        selected_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export result", DEFAULT_EXPORT_NAME, ";;".join(EXPORT_FILTERS)
        )
        if not selected_path:
            return
        destination = Path(selected_path)
        if not destination.suffix:
            destination = destination.with_suffix(EXPORT_FILTERS[selected_filter])
        self._controller.export_last_result(destination)

    def _on_export_chart_clicked(self) -> None:
        selected_path, _ = QFileDialog.getSaveFileName(
            self, "Export chart", DEFAULT_CHART_NAME, CHART_FILTER
        )
        if not selected_path:
            return
        self._pending_chart_destination = Path(selected_path).with_suffix(CHART_SUFFIX)
        self._show_building_chart_state()
        self._controller.build_overview()

    def _show_building_chart_state(self) -> None:
        self._set_configuration_enabled(False)
        self._load_button.setEnabled(False)
        self._set_exports_enabled(False)
        self._status_label.setText("Building chart…")

    def _save_overview_chart(self, overview: MetricOverview) -> None:
        destination = self._pending_chart_destination
        self._show_ready_state()
        self._set_exports_enabled(True)
        if destination is None:
            return
        if not render_overview_chart(overview).save(str(destination)):
            self._status_label.setText("Failed.")
            QMessageBox.critical(self, WINDOW_TITLE, f"Could not save the chart to {destination}.")
            return
        self._status_label.setText(f"Chart saved to {destination}")

    def _show_overview_failure(self, message: str) -> None:
        self._show_ready_state()
        self._set_exports_enabled(True)
        self._status_label.setText("Failed.")
        QMessageBox.critical(self, WINDOW_TITLE, message)

    def _show_awaiting_dataset_state(self) -> None:
        self._set_configuration_enabled(False)
        self._load_button.setEnabled(True)
        self._cancel_button.setEnabled(False)
        self._set_exports_enabled(False)
        self._set_results_enabled(False)
        self._progress_bar.setValue(0)
        self._status_label.clear()
        self._dataset_label.setText(NO_DATASET_TEXT)

    def _show_ready_state(self) -> None:
        self._set_configuration_enabled(True)
        self._load_button.setEnabled(True)
        self._cancel_button.setEnabled(False)
        self._set_exports_enabled(False)

    def _show_running_state(self, status_text: str, is_cancellable: bool) -> None:
        self._set_configuration_enabled(False)
        self._load_button.setEnabled(False)
        self._cancel_button.setEnabled(is_cancellable)
        self._set_exports_enabled(False)
        self._clear_results()
        self._progress_bar.setValue(0)
        self._status_label.setText(status_text)

    def _show_dataset_loaded(self, source: str, question_count: int) -> None:
        self._clear_results()
        self._progress_bar.setValue(0)
        self._status_label.clear()
        self._dataset_label.setText(f"{Path(source).name} · {question_count} questions")
        self._dataset_label.setToolTip(source)
        self._show_ready_state()

    def _show_dataset_failure(self, message: str) -> None:
        QMessageBox.critical(self, WINDOW_TITLE, message)

    def _show_progress(self, completed: int, total: int) -> None:
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(completed)
        self._status_label.setText(f"Question {completed} of {total}")

    def _show_result(self, result: EvaluationResult) -> None:
        self._show_ready_state()
        self._set_exports_enabled(True)
        self._select_method_silently(result.method.identifier)
        self._set_score_header(result.method.column_header)
        self._fill_table(result)
        self._metrics_panel.show_metrics(result.metrics, result.method)
        self._average_label.setText(self._describe_average(result))
        self._set_results_enabled(True)
        self._status_label.setText("Done.")

    def _show_failure(self, message: str) -> None:
        self._show_ready_state()
        self._status_label.setText("Failed.")
        QMessageBox.critical(self, WINDOW_TITLE, message)

    def _show_cancelled(self) -> None:
        self._show_ready_state()
        self._status_label.setText("Cancelled.")

    def _show_export_success(self, destination: str) -> None:
        self._status_label.setText(f"Result saved to {destination}")

    def _show_export_failure(self, message: str) -> None:
        QMessageBox.critical(self, WINDOW_TITLE, message)

    def _set_configuration_enabled(self, is_enabled: bool) -> None:
        configuration_widgets = (
            self._endpoint_input,
            self._api_key_input,
            self._model_input,
            self._method_combo,
            self._run_button,
        )
        for widget in configuration_widgets:
            widget.setEnabled(is_enabled)

    def _set_exports_enabled(self, is_enabled: bool) -> None:
        for widget in (self._export_button, self._chart_button):
            widget.setEnabled(is_enabled)

    def _set_results_enabled(self, is_enabled: bool) -> None:
        for widget in (self._table, self._metrics_panel, self._average_label):
            widget.setEnabled(is_enabled)

    def _clear_results(self) -> None:
        self._table.setRowCount(0)
        self._metrics_panel.clear()
        self._average_label.clear()
        self._set_results_enabled(False)

    def _select_method_silently(self, identifier: str) -> None:
        self._method_combo.blockSignals(True)
        self._method_combo.setCurrentIndex(self._method_combo.findData(identifier))
        self._method_combo.blockSignals(False)

    def _set_score_header(self, header: str) -> None:
        self._table.setHorizontalHeaderLabels([*FIXED_TABLE_HEADERS, header])

    def _describe_average(self, result: EvaluationResult) -> str:
        header = result.method.column_header
        if result.method.score_kind is ScoreKind.BINARY:
            correct_count = result.metrics.correct_count
            rate = PERCENTAGE_FORMAT.format(result.average_score)
            return f"{header}: {rate} ({correct_count} of {len(result.scores)})"
        return f"Average {header}: {CONTINUOUS_SCORE_FORMAT.format(result.average_score)}"

    def _fill_table(self, result: EvaluationResult) -> None:
        score_format = (
            BINARY_SCORE_FORMAT if result.method.score_kind is ScoreKind.BINARY else CONTINUOUS_SCORE_FORMAT
        )
        self._table.setRowCount(len(result.scores))
        for row, score in enumerate(result.scores):
            self._table.setItem(row, 0, QTableWidgetItem(score.question.text))
            self._table.setItem(row, 1, QTableWidgetItem(score.question.expected_answer))
            self._table.setItem(row, 2, QTableWidgetItem(score.given_answer))
            score_item = QTableWidgetItem(score_format.format(score.score))
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, SCORE_COLUMN, score_item)
        self._table.resizeRowsToContents()

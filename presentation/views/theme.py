from string import Template

from presentation.views.branding import (
    ACCENT_BLUE,
    DIAGONAL_GRADIENT,
    DISABLED_TEXT_COLOR,
    GRADIENT_END,
    SOFT_BLUE,
    TEXT_COLOR,
)

_MAIN_WINDOW_TEMPLATE = Template(
    """
QMainWindow, QMessageBox {
    background: $gradient;
}
QLabel {
    color: $text;
}
QLabel:disabled {
    color: $disabled_text;
}
QLabel#brandTitle {
    color: white;
    font-size: 22px;
    font-weight: 700;
}
QLabel#brandSubtitle, QLabel#datasetLabel, QLabel#statusLabel {
    color: $soft_blue;
}
QLabel#brandSubtitle {
    font-size: 12px;
}
QLabel#demoBadge {
    color: $soft_blue;
    background: rgba(255, 255, 255, 10%);
    border: 1px solid rgba(255, 255, 255, 28%);
    border-radius: 12px;
    padding: 5px 14px;
    font-weight: 600;
}
QLabel#averageLabel {
    color: white;
}
QLabel#averageLabel:disabled {
    color: $disabled_text;
}
QLabel#metricCaption {
    color: $soft_blue;
    font-size: 11px;
}
QLabel#metricValue {
    color: white;
}
QLabel#metricCaption:disabled, QLabel#metricValue:disabled {
    color: $disabled_text;
}
QLineEdit {
    background: rgba(255, 255, 255, 9%);
    border: 1px solid rgba(255, 255, 255, 22%);
    border-radius: 8px;
    padding: 7px 10px;
    color: white;
    selection-background-color: $accent;
    placeholder-text-color: rgba(255, 255, 255, 45%);
}
QLineEdit:focus {
    border: 1px solid $accent;
}
QLineEdit:disabled {
    background: rgba(255, 255, 255, 4%);
    border: 1px solid rgba(255, 255, 255, 10%);
    color: $disabled_text;
    placeholder-text-color: rgba(255, 255, 255, 20%);
}
QComboBox {
    background: rgba(255, 255, 255, 9%);
    border: 1px solid rgba(255, 255, 255, 22%);
    border-radius: 8px;
    padding: 7px 10px;
    color: white;
}
QComboBox:focus, QComboBox:on {
    border: 1px solid $accent;
}
QComboBox:disabled {
    background: rgba(255, 255, 255, 4%);
    border: 1px solid rgba(255, 255, 255, 10%);
    color: $disabled_text;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background: #0f172a;
    color: white;
    border: 1px solid rgba(255, 255, 255, 22%);
    selection-background-color: $blue;
    selection-color: white;
    outline: none;
}
QPushButton {
    background: rgba(255, 255, 255, 10%);
    border: 1px solid rgba(255, 255, 255, 24%);
    border-radius: 8px;
    padding: 7px 18px;
    color: white;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 18%);
}
QPushButton:pressed {
    background: rgba(255, 255, 255, 6%);
}
QPushButton:disabled {
    background: rgba(255, 255, 255, 4%);
    border: 1px solid rgba(255, 255, 255, 10%);
    color: $disabled_text;
}
QPushButton#primaryButton {
    background: white;
    border: 1px solid white;
    color: $blue;
    font-weight: 700;
}
QPushButton#primaryButton:hover {
    background: #e0ecff;
}
QPushButton#primaryButton:pressed {
    background: $soft_blue;
}
QPushButton#primaryButton:disabled {
    background: rgba(255, 255, 255, 12%);
    border: 1px solid rgba(255, 255, 255, 10%);
    color: $disabled_text;
}
QProgressBar {
    background: rgba(255, 255, 255, 14%);
    border: none;
    border-radius: 4px;
    min-height: 8px;
    max-height: 8px;
}
QProgressBar::chunk {
    background: white;
    border-radius: 4px;
}
QTableWidget {
    background: rgba(15, 23, 42, 45%);
    alternate-background-color: rgba(255, 255, 255, 5%);
    color: $text;
    gridline-color: rgba(255, 255, 255, 8%);
    border: 1px solid rgba(255, 255, 255, 14%);
    border-radius: 10px;
    selection-background-color: rgba(96, 165, 250, 35%);
    selection-color: white;
}
QTableWidget:disabled {
    color: $disabled_text;
}
QHeaderView {
    background: transparent;
    border: none;
}
QHeaderView::section {
    background: rgba(255, 255, 255, 10%);
    color: $soft_blue;
    padding: 8px;
    border: none;
    font-weight: 600;
}
QHeaderView::section:vertical {
    background: rgba(255, 255, 255, 6%);
    padding: 4px 10px;
    font-weight: 400;
}
QHeaderView::section:disabled {
    color: $disabled_text;
}
QTableCornerButton::section {
    background: transparent;
    border: none;
}
QFrame#metricsPanel {
    background: rgba(255, 255, 255, 7%);
    border: 1px solid rgba(255, 255, 255, 14%);
    border-radius: 12px;
}
QFrame#metricsPanel:disabled {
    background: rgba(255, 255, 255, 3%);
    border: 1px solid rgba(255, 255, 255, 8%);
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 28%);
    border-radius: 4px;
    min-height: 24px;
    min-width: 24px;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}
"""
)

MAIN_WINDOW_STYLE = _MAIN_WINDOW_TEMPLATE.substitute(
    gradient=DIAGONAL_GRADIENT,
    text=TEXT_COLOR,
    disabled_text=DISABLED_TEXT_COLOR,
    soft_blue=SOFT_BLUE,
    accent=ACCENT_BLUE,
    blue=GRADIENT_END,
)

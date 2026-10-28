from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

BAR_HEIGHT_RATIOS = (0.38, 0.62, 0.86)
CORNER_RADIUS_RATIO = 0.26
PADDING_RATIO = 0.2
BAR_WIDTH_RATIO = 0.14
WHITE = QColor(255, 255, 255)
BACKGROUND_COLOR = QColor(255, 255, 255, 38)


def draw_logo(painter: QPainter, size: float) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(BACKGROUND_COLOR)
    corner_radius = size * CORNER_RADIUS_RATIO
    painter.drawRoundedRect(QRectF(0, 0, size, size), corner_radius, corner_radius)
    painter.setBrush(WHITE)
    padding = size * PADDING_RATIO
    bar_width = size * BAR_WIDTH_RATIO
    gap = (size - 2 * padding - 3 * bar_width) / 2
    usable_height = size - 2 * padding
    for index, ratio in enumerate(BAR_HEIGHT_RATIOS):
        bar_height = usable_height * ratio
        left = padding + index * (bar_width + gap)
        top = padding + usable_height - bar_height
        painter.drawRoundedRect(QRectF(left, top, bar_width, bar_height), bar_width / 2, bar_width / 2)
    painter.restore()


class LogoMark(QWidget):
    def __init__(self, size: int):
        super().__init__()
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:
        draw_logo(QPainter(self), self._size)

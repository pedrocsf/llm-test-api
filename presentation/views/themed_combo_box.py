from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QComboBox

from presentation.views.branding import SOFT_BLUE

CHEVRON_RIGHT_OFFSET = 18
CHEVRON_HALF_WIDTH = 5.0
CHEVRON_HALF_HEIGHT = 2.5
CHEVRON_LINE_WIDTH = 1.8
DISABLED_CHEVRON_COLOR = QColor(255, 255, 255, 70)


class ThemedComboBox(QComboBox):
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(SOFT_BLUE) if self.isEnabled() else DISABLED_CHEVRON_COLOR
        painter.setPen(QPen(color, CHEVRON_LINE_WIDTH, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        center_x = self.width() - CHEVRON_RIGHT_OFFSET
        center_y = self.height() / 2
        painter.drawPolyline(
            [
                QPointF(center_x - CHEVRON_HALF_WIDTH, center_y - CHEVRON_HALF_HEIGHT),
                QPointF(center_x, center_y + CHEVRON_HALF_HEIGHT),
                QPointF(center_x + CHEVRON_HALF_WIDTH, center_y - CHEVRON_HALF_HEIGHT),
            ]
        )

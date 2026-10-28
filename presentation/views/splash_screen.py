from PySide6.QtCore import QElapsedTimer, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QGuiApplication, QPainter
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QMessageBox, QVBoxLayout, QWidget

from presentation.views.branding import (
    APPLICATION_NAME,
    APPLICATION_SUBTITLE,
    DIAGONAL_GRADIENT,
    PALE_BLUE,
    SOFT_BLUE,
)
from presentation.views.logo_mark import LogoMark

LOADING_STATUS = "Loading embedding model…"
SPLASH_WIDTH = 480
SPLASH_HEIGHT = 300
SHADOW_MARGIN = 24
LOGO_SIZE = 76
LOADING_BAR_HEIGHT = 6
LOADING_BAR_CYCLE_MILLISECONDS = 1400
LOADING_BAR_SEGMENT_RATIO = 0.35
LOADING_BAR_FRAME_MILLISECONDS = 16
WHITE = QColor(255, 255, 255)
TRACK_COLOR = QColor(255, 255, 255, 46)

PANEL_STYLE = (
    "#panel { background: " + DIAGONAL_GRADIENT + "; border-radius: 22px; }"
    "QLabel#title { color: white; font-size: 30px; font-weight: 700; }"
    "QLabel#subtitle { color: " + SOFT_BLUE + "; font-size: 14px; }"
    "QLabel#status { color: " + PALE_BLUE + "; font-size: 12px; }"
)


class LoadingBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(LOADING_BAR_HEIGHT)
        self._clock = QElapsedTimer()
        self._clock.start()
        self._frame_timer = QTimer(self)
        self._frame_timer.timeout.connect(self.update)
        self._frame_timer.start(LOADING_BAR_FRAME_MILLISECONDS)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        radius = self.height() / 2
        painter.setBrush(TRACK_COLOR)
        painter.drawRoundedRect(QRectF(self.rect()), radius, radius)
        painter.setClipRect(self.rect())
        painter.setBrush(WHITE)
        painter.drawRoundedRect(self._segment_rectangle(), radius, radius)

    def _segment_rectangle(self) -> QRectF:
        segment_width = self.width() * LOADING_BAR_SEGMENT_RATIO
        progress = (self._clock.elapsed() % LOADING_BAR_CYCLE_MILLISECONDS) / LOADING_BAR_CYCLE_MILLISECONDS
        left = -segment_width + progress * (self.width() + segment_width)
        return QRectF(left, 0, segment_width, self.height())


class SplashScreen(QWidget):
    def __init__(self, status_text: str = LOADING_STATUS):
        super().__init__()
        self._status_text = status_text
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(SPLASH_WIDTH + 2 * SHADOW_MARGIN, SPLASH_HEIGHT + 2 * SHADOW_MARGIN)
        self._build_interface()
        self._center_on_screen()

    def show_failure(self, message: str) -> None:
        self.close()
        QMessageBox.critical(None, APPLICATION_NAME, message)

    def _build_interface(self) -> None:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setStyleSheet(PANEL_STYLE)
        panel.setGraphicsEffect(self._build_shadow())
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(40, 36, 40, 32)
        panel_layout.addWidget(LogoMark(LOGO_SIZE), alignment=Qt.AlignmentFlag.AlignHCenter)
        panel_layout.addSpacing(14)
        panel_layout.addWidget(self._build_label("title", APPLICATION_NAME), alignment=Qt.AlignmentFlag.AlignHCenter)
        panel_layout.addWidget(
            self._build_label("subtitle", APPLICATION_SUBTITLE), alignment=Qt.AlignmentFlag.AlignHCenter
        )
        panel_layout.addStretch(1)
        panel_layout.addWidget(LoadingBar())
        panel_layout.addSpacing(10)
        panel_layout.addWidget(self._build_label("status", self._status_text), alignment=Qt.AlignmentFlag.AlignHCenter)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN)
        outer_layout.addWidget(panel)

    def _build_label(self, object_name: str, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName(object_name)
        return label

    def _build_shadow(self) -> QGraphicsDropShadowEffect:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(SHADOW_MARGIN * 1.5)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 110))
        return shadow

    def _center_on_screen(self) -> None:
        screen_center = QGuiApplication.primaryScreen().availableGeometry().center()
        frame = self.frameGeometry()
        frame.moveCenter(screen_center)
        self.move(frame.topLeft())

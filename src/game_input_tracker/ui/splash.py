from __future__ import annotations

from importlib.resources import files

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class SplashScreen(QWidget):
    def __init__(self, icon: QIcon | None = None) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.SplashScreen
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(760, 440)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.setInterval(32)
        self._timer.timeout.connect(self._tick)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 54, 48, 46)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        source_icon = icon if icon and not icon.isNull() else QIcon(str(files("game_input_tracker").joinpath("assets/keypulse-icon.png")))
        self.icon_label.setPixmap(source_icon.pixmap(96, 96))

        self.title = QLabel("KEY PULSE")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI Variable Display", 42, QFont.Weight.Black)
        self.title.setFont(title_font)
        self.title.setStyleSheet("color: #e8fbff; background: transparent;")

        self.credit = QLabel("Developed by MEMPHIS HYDRA")
        self.credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit_font = QFont("Segoe UI", 12, QFont.Weight.DemiBold)
        self.credit.setFont(credit_font)
        self.credit.setStyleSheet("color: #f7b955; background: transparent;")

        self.status = QLabel("Initializing local session engine")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: #8da2b8; background: transparent;")

        layout.addStretch(1)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title)
        layout.addWidget(self.credit)
        layout.addSpacing(36)
        layout.addWidget(self.status)
        layout.addStretch(1)

    def show_centered(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.move(geometry.center() - self.rect().center())
        self._timer.start()
        self.show()

    def closeEvent(self, event) -> None:
        self._timer.stop()
        super().closeEvent(event)

    def _tick(self) -> None:
        self._phase = (self._phase + 1) % 180
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        panel = QRectF(8, 8, self.width() - 16, self.height() - 16)
        painter.setBrush(QColor("#0a0f15"))
        painter.setPen(QPen(QColor("#263648"), 1.5))
        painter.drawRoundedRect(panel, 34, 34)

        glow_alpha = 90 + int(60 * abs(90 - self._phase) / 90)
        painter.setPen(QPen(QColor(34, 211, 238, glow_alpha), 3))
        painter.drawRoundedRect(panel.adjusted(2, 2, -2, -2), 31, 31)

        line_y = self.height() - 94
        start_x = 142
        points = [
            (start_x, line_y),
            (start_x + 110, line_y),
            (start_x + 136, line_y - 24),
            (start_x + 166, line_y + 34),
            (start_x + 216, line_y - 62),
            (start_x + 266, line_y + 24),
            (start_x + 300, line_y),
            (self.width() - 142, line_y),
        ]
        painter.setPen(
            QPen(
                QColor("#22d3ee"),
                5,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        for first, second in zip(points, points[1:]):
            painter.drawLine(first[0], first[1], second[0], second[1])

        highlight_x = start_x + ((self._phase * 4) % max(1, self.width() - 284))
        painter.setPen(QPen(QColor("#f59e0b"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(highlight_x, line_y + 32, min(highlight_x + 72, self.width() - 142), line_y + 32)

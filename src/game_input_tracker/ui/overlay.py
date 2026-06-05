from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget


class InputOverlay(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("KeyPulse Overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(520, 260)
        self._active_inputs: set[str] = set()

    def set_overlay_visible(self, visible: bool) -> None:
        if visible:
            self._center_near_bottom()
            self.show()
        else:
            self.hide()

    def set_active_inputs(self, active_inputs: object) -> None:
        self._active_inputs = set(active_inputs or [])
        self.update()

    def _center_near_bottom(self) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geometry = screen.availableGeometry()
        x = geometry.center().x() - self.width() // 2
        y = geometry.bottom() - self.height() - 72
        self.move(x, y)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        panel = QRectF(8, 8, self.width() - 16, self.height() - 16)
        painter.setBrush(QColor(10, 15, 21, 216))
        painter.setPen(QPen(QColor("#2b3b4e"), 1.4))
        painter.drawRoundedRect(panel, 18, 18)

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor("#7dd3fc"))
        painter.drawText(QRectF(26, 20, self.width() - 52, 24), Qt.AlignmentFlag.AlignLeft, "KEYPULSE LIVE INPUT")

        keys = [
            ("W", 214, 58, 56, 40),
            ("A", 152, 104, 56, 40),
            ("S", 214, 104, 56, 40),
            ("D", 276, 104, 56, 40),
            ("Shift", 88, 150, 96, 40),
            ("Space", 190, 150, 166, 40),
            ("Ctrl", 362, 150, 70, 40),
            ("Left Click", 66, 74, 106, 40),
            ("Right Click", 348, 74, 106, 40),
            ("Scroll Up", 66, 202, 106, 34),
            ("Scroll Down", 348, 202, 106, 34),
        ]
        for label, x, y, width, height in keys:
            self._draw_button(painter, label, x, y, width, height)

    def _draw_button(
        self,
        painter: QPainter,
        label: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        active = label in self._active_inputs
        fill = QColor("#22d3ee") if active else QColor(23, 32, 43, 224)
        border = QColor("#a5f3fc") if active else QColor("#334155")
        text = QColor("#061018") if active else QColor("#e6eef7")
        painter.setBrush(fill)
        painter.setPen(QPen(border, 1.6))
        painter.drawRoundedRect(QRectF(x, y, width, height), 8, 8)
        painter.setPen(text)
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        painter.drawText(QRectF(x, y, width, height), Qt.AlignmentFlag.AlignCenter, label)

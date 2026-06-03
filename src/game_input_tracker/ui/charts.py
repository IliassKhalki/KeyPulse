from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class BarChart(QWidget):
    def __init__(self, title: str = "", parent=None) -> None:
        super().__init__(parent)
        self._title = title
        self._data: list[tuple[str, int]] = []
        self.setMinimumHeight(220)

    def set_data(self, data: list[tuple[str, int]]) -> None:
        self._data = data
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(16, 16, -16, -16)
        painter.setPen(QColor("#d6e2ef"))
        painter.drawText(rect.left(), rect.top(), self._title)

        chart_rect = rect.adjusted(0, 28, 0, -8)
        if not self._data:
            painter.setPen(QColor("#738398"))
            painter.drawText(chart_rect, Qt.AlignCenter, "No data yet")
            return

        max_value = max(value for _, value in self._data) or 1
        gap = 8
        bar_width = max(18, int((chart_rect.width() - gap * (len(self._data) - 1)) / len(self._data)))
        x = chart_rect.left()
        for label, value in self._data:
            height_ratio = value / max_value
            bar_height = max(4, int(chart_rect.height() * height_ratio * 0.78))
            bar_rect = QRectF(x, chart_rect.bottom() - bar_height - 24, bar_width, bar_height)
            painter.setBrush(QColor("#22d3ee"))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(bar_rect, 4, 4)
            painter.setPen(QColor("#9fb0c3"))
            painter.drawText(QRectF(x, chart_rect.bottom() - 20, bar_width, 18), Qt.AlignCenter, label[:7])
            x += bar_width + gap


class Heatmap(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._keys: list[tuple[str, int]] = []
        self.setMinimumHeight(180)

    def set_keys(self, keys: list[tuple[str, int]]) -> None:
        self._keys = keys
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(16, 16, -16, -16)
        painter.setPen(QColor("#d6e2ef"))
        painter.drawText(rect.left(), rect.top(), "Keyboard Heatmap")
        keys = self._keys or []
        values = dict(keys)
        max_value = max(values.values()) if values else 1
        rows = [
            ["Esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["Caps Lock", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Enter"],
            ["Shift", "Z", "X", "C", "V", "B", "N", "M", "Backspace"],
            ["Ctrl", "Alt", "Space", "Left Click", "Right Click"],
        ]
        y = rect.top() + 30
        for row in rows:
            x = rect.left()
            for key in row:
                count = values.get(key, 0)
                intensity = min(1.0, count / max_value) if max_value else 0
                color = QColor("#1b2633")
                if count:
                    color = QColor.fromRgbF(0.10 + 0.85 * intensity, 0.34 + 0.30 * intensity, 0.38)
                width = 48 if len(key) <= 5 else 78
                if key == "Space":
                    width = 180
                painter.setBrush(color)
                painter.setPen(QPen(QColor("#334155"), 1))
                painter.drawRoundedRect(QRectF(x, y, width, 26), 5, 5)
                painter.setPen(QColor("#f8fbff"))
                painter.drawText(QRectF(x, y, width, 26), Qt.AlignCenter, key)
                x += width + 6
            y += 34

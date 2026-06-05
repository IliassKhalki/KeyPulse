from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen
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
        self.setFixedSize(900, 480)
        self._active_inputs: set[str] = set()
        self._controller_inputs: set[str] = set()
        self._drag_origin: QPoint | None = None
        self._was_positioned_by_user = False

    def set_overlay_visible(self, visible: bool) -> None:
        if visible:
            if not self._was_positioned_by_user:
                self._center_near_bottom()
            self.show()
        else:
            self.hide()

    def set_active_inputs(self, active_inputs: object) -> None:
        self._active_inputs = set(active_inputs or [])
        self.update()

    def set_controller_inputs(self, active_inputs: object) -> None:
        self._controller_inputs = set(active_inputs or [])
        self._resize_for_controller()
        self.update()

    def _center_near_bottom(self) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geometry = screen.availableGeometry()
        x = max(geometry.left() + 16, geometry.center().x() - self.width() // 2)
        y = max(geometry.top() + 24, geometry.bottom() - self.height() - 48)
        self.move(x, y)

    def _resize_for_controller(self) -> None:
        target_width = 1180 if self._controller_connected else 900
        target_height = 560 if self._controller_connected else 480
        if self.width() == target_width and self.height() == target_height:
            return
        old_center = self.geometry().center()
        self.setFixedSize(target_width, target_height)
        if self._was_positioned_by_user:
            self.move(old_center - self.rect().center())
        elif self.isVisible():
            self._center_near_bottom()

    @property
    def _controller_connected(self) -> bool:
        return "Controller Connected" in self._controller_inputs

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        panel = QRectF(8, 8, self.width() - 16, self.height() - 16)
        painter.setBrush(QColor(10, 15, 21, 168))
        painter.setPen(QPen(QColor(43, 59, 78, 150), 1.2))
        painter.drawRoundedRect(panel, 20, 20)

        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor("#7dd3fc"))
        painter.drawText(QRectF(28, 22, 540, 26), Qt.AlignmentFlag.AlignLeft, "KEYPULSE LIVE INPUT")
        painter.setPen(QColor("#f7b955"))
        header = "DRAG TO MOVE"
        if self._controller_connected:
            header = "FULL KEYBOARD + XINPUT CONTROLLER"
        painter.drawText(QRectF(self.width() - 460, 22, 420, 26), Qt.AlignmentFlag.AlignRight, header)

        self._draw_keyboard(painter)
        if self._controller_connected:
            self._draw_controller(painter)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
            self._was_positioned_by_user = True
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = None
            self._was_positioned_by_user = True
            event.accept()

    def _draw_keyboard(self, painter: QPainter) -> None:
        x0 = 34
        y0 = 66
        unit = 44
        gap = 6
        rows = [
            [
                ("Esc", 1.2),
                ("`", 1),
                ("1", 1),
                ("2", 1),
                ("3", 1),
                ("4", 1),
                ("5", 1),
                ("6", 1),
                ("7", 1),
                ("8", 1),
                ("9", 1),
                ("0", 1),
                ("-", 1),
                ("=", 1),
                ("Backspace", 2.1),
            ],
            [
                ("Tab", 1.45),
                ("Q", 1),
                ("W", 1),
                ("E", 1),
                ("R", 1),
                ("T", 1),
                ("Y", 1),
                ("U", 1),
                ("I", 1),
                ("O", 1),
                ("P", 1),
                ("[", 1),
                ("]", 1),
                ("\\", 1.55),
            ],
            [
                ("Caps Lock", 1.8),
                ("A", 1),
                ("S", 1),
                ("D", 1),
                ("F", 1),
                ("G", 1),
                ("H", 1),
                ("J", 1),
                ("K", 1),
                ("L", 1),
                (";", 1),
                ("'", 1),
                ("Enter", 2.15),
            ],
            [
                ("Shift", 2.35),
                ("Z", 1),
                ("X", 1),
                ("C", 1),
                ("V", 1),
                ("B", 1),
                ("N", 1),
                ("M", 1),
                (",", 1),
                (".", 1),
                ("/", 1),
                ("Shift", 2.6),
            ],
            [
                ("Ctrl", 1.4),
                ("Windows", 1.4),
                ("Alt", 1.4),
                ("Space", 6.2),
                ("Alt", 1.4),
                ("Ctrl", 1.4),
                ("Left", 1),
                ("Up", 1),
                ("Down", 1),
                ("Right", 1),
            ],
        ]
        for row_index, row in enumerate(rows):
            x = x0
            y = y0 + row_index * 56
            for label, span in row:
                width = int(unit * span + gap * (span - 1))
                self._draw_key(painter, label, x, y, width, 42)
                x += width + gap

        mouse_y = 390
        self._draw_key(painter, "Left Click", 42, mouse_y, 126, 42)
        self._draw_key(painter, "Middle Click", 176, mouse_y, 136, 42)
        self._draw_key(painter, "Right Click", 320, mouse_y, 136, 42)
        self._draw_key(painter, "Scroll Up", 464, mouse_y, 126, 42)
        self._draw_key(painter, "Scroll Down", 598, mouse_y, 136, 42)

    def _draw_controller(self, painter: QPainter) -> None:
        x = 795
        y = 300
        painter.setPen(QColor("#9fb0c3"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        status = "Controller connected" if "Controller Connected" in self._controller_inputs else "No XInput controller"
        painter.drawText(QRectF(x, y - 30, 360, 22), Qt.AlignmentFlag.AlignLeft, status)

        painter.setBrush(QColor(18, 27, 38, 176))
        painter.setPen(QPen(QColor(52, 70, 92, 170), 1.5))
        painter.drawRoundedRect(QRectF(x + 25, y + 22, 330, 168), 64, 64)

        self._draw_stick(painter, "LS", x + 92, y + 110)
        self._draw_stick(painter, "RS", x + 244, y + 140)
        self._draw_dpad(painter, x + 54, y + 38)
        self._draw_face_buttons(painter, x + 270, y + 52)
        self._draw_controller_button(painter, "Back", x + 156, y + 78, 52, 30)
        self._draw_controller_button(painter, "Start", x + 216, y + 78, 52, 30)
        self._draw_controller_button(painter, "LB/L1", x + 58, y + 0, 92, 30)
        self._draw_controller_button(painter, "RB/R1", x + 230, y + 0, 92, 30)
        self._draw_controller_button(painter, "LT/L2", x + 58, y + 198, 92, 30)
        self._draw_controller_button(painter, "RT/R2", x + 230, y + 198, 92, 30)

    def _draw_key(self, painter: QPainter, label: str, x: int, y: int, width: int, height: int) -> None:
        active = label in self._active_inputs
        fill = QColor("#22d3ee") if active else QColor(23, 32, 43, 150)
        border = QColor("#a5f3fc") if active else QColor(51, 65, 85, 155)
        text = QColor("#061018") if active else QColor("#e6eef7")
        painter.setBrush(fill)
        painter.setPen(QPen(border, 1.5))
        painter.drawRoundedRect(QRectF(x, y, width, height), 7, 7)
        painter.setPen(text)
        painter.setFont(QFont("Segoe UI", 8 if len(label) > 7 else 9, QFont.Weight.DemiBold))
        painter.drawText(QRectF(x + 2, y, width - 4, height), Qt.AlignmentFlag.AlignCenter, label)

    def _draw_controller_button(
        self,
        painter: QPainter,
        label: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        active = label in self._controller_inputs
        fill = QColor("#f59e0b") if active else QColor(28, 39, 52, 158)
        border = QColor("#fde68a") if active else QColor(69, 86, 109, 155)
        text = QColor("#111827") if active else QColor("#e6eef7")
        painter.setBrush(fill)
        painter.setPen(QPen(border, 1.4))
        painter.drawRoundedRect(QRectF(x, y, width, height), 8, 8)
        painter.setPen(text)
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(QRectF(x, y, width, height), Qt.AlignmentFlag.AlignCenter, label)

    def _draw_face_buttons(self, painter: QPainter, x: int, y: int) -> None:
        self._draw_round_button(painter, "Y/Triangle", "Y", x + 38, y, "#f7d154")
        self._draw_round_button(painter, "X/Square", "X", x, y + 36, "#60a5fa")
        self._draw_round_button(painter, "B/Circle", "B", x + 76, y + 36, "#fb7185")
        self._draw_round_button(painter, "A/Cross", "A", x + 38, y + 72, "#34d399")

    def _draw_round_button(
        self,
        painter: QPainter,
        active_label: str,
        visible_label: str,
        x: int,
        y: int,
        color: str,
    ) -> None:
        active = active_label in self._controller_inputs
        painter.setBrush(QColor(color) if active else QColor(28, 39, 52, 158))
        painter.setPen(QPen(QColor("#e5e7eb") if active else QColor(69, 86, 109, 155), 1.4))
        painter.drawEllipse(QPointF(x + 16, y + 16), 16, 16)
        painter.setPen(QColor("#071018") if active else QColor("#e6eef7"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(x, y, 32, 32), Qt.AlignmentFlag.AlignCenter, visible_label)

    def _draw_stick(self, painter: QPainter, prefix: str, cx: int, cy: int) -> None:
        active = any(
            label in self._controller_inputs
            for label in (f"{prefix} Up", f"{prefix} Down", f"{prefix} Left", f"{prefix} Right")
        )
        painter.setBrush(QColor("#22d3ee") if active else QColor(12, 18, 26, 168))
        painter.setPen(QPen(QColor("#a5f3fc") if active else QColor(69, 86, 109, 155), 2))
        painter.drawEllipse(QPointF(cx, cy), 30, 30)
        painter.setPen(QColor("#061018") if active else QColor("#e6eef7"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(cx - 30, cy - 12, 60, 24), Qt.AlignmentFlag.AlignCenter, prefix)
        if f"{prefix} Up" in self._controller_inputs:
            painter.drawLine(cx, cy - 44, cx, cy - 32)
        if f"{prefix} Down" in self._controller_inputs:
            painter.drawLine(cx, cy + 32, cx, cy + 44)
        if f"{prefix} Left" in self._controller_inputs:
            painter.drawLine(cx - 44, cy, cx - 32, cy)
        if f"{prefix} Right" in self._controller_inputs:
            painter.drawLine(cx + 32, cy, cx + 44, cy)

    def _draw_dpad(self, painter: QPainter, x: int, y: int) -> None:
        self._draw_controller_button(painter, "D-Up", x + 34, y, 34, 34)
        self._draw_controller_button(painter, "D-Left", x, y + 34, 34, 34)
        self._draw_controller_button(painter, "D-Right", x + 68, y + 34, 34, 34)
        self._draw_controller_button(painter, "D-Down", x + 34, y + 68, 34, 34)

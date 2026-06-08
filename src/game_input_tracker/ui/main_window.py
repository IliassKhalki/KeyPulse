from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from game_input_tracker.core.formatting import compact_number, format_duration
from game_input_tracker.data.repository import TrackerRepository
from game_input_tracker.ui.charts import BarChart, Heatmap


class MetricCard(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setProperty("panel", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        self.label = QLabel(label)
        self.label.setProperty("muted", True)
        self.value = QLabel("0")
        self.value.setProperty("metric", True)
        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def set_value(self, value: str) -> None:
        self.value.setText(value)


class MainWindow(QMainWindow):
    refresh_requested = Signal()
    startup_toggled = Signal(bool)
    overlay_toggled = Signal(bool)

    def __init__(self, repository: TrackerRepository) -> None:
        super().__init__()
        self.repository = repository
        self.setWindowTitle("KeyPulse")
        self.resize(1180, 760)
        self._session_started_at: datetime | None = None

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(24, 22, 24, 24)
        self.content_layout.setSpacing(18)
        scroll.setWidget(content)
        root_layout.addWidget(scroll)
        self.setCentralWidget(root)

        self._build_header()
        self._build_metrics()
        self._build_charts()
        self._build_tables()

    def _build_header(self) -> None:
        row = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("KeyPulse")
        title.setProperty("brand", True)
        self.subtitle = QLabel("Ready to measure your next session")
        self.subtitle.setProperty("muted", True)
        title_box.addWidget(title)
        title_box.addWidget(self.subtitle)

        self.current_game = QLabel("No active game")
        self.current_game.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.current_game.setProperty("title", True)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_requested.emit)
        self.startup = QCheckBox("Start with Windows")
        self.startup.toggled.connect(self.startup_toggled.emit)
        self.overlay = QPushButton("Overlay")
        self.overlay.setCheckable(True)
        self.overlay.toggled.connect(self.overlay_toggled.emit)

        row.addLayout(title_box, 1)
        row.addWidget(self.startup)
        row.addWidget(self.overlay)
        row.addWidget(refresh)
        row.addWidget(self.current_game)
        self.content_layout.addLayout(row)

    def _build_metrics(self) -> None:
        grid = QGridLayout()
        grid.setSpacing(12)
        self.playtime = MetricCard("Total Playtime")
        self.keyboard = MetricCard("Keyboard Presses")
        self.mouse = MetricCard("Mouse Inputs")
        self.games = MetricCard("Games Tracked")
        self.session_duration = MetricCard("This Session")
        self.session_keys = MetricCard("Current Session Keys")
        self.session_mouse = MetricCard("Current Session Mouse")
        cards = [
            self.playtime,
            self.keyboard,
            self.mouse,
            self.games,
            self.session_duration,
            self.session_keys,
            self.session_mouse,
        ]
        for index, card in enumerate(cards):
            grid.addWidget(card, index // 3, index % 3)
        self.content_layout.addLayout(grid)

    def _build_charts(self) -> None:
        row = QHBoxLayout()
        self.top_games_chart = BarChart("Most Played Games")
        self.top_keys_chart = BarChart("Most Used Keys")
        self.heatmap = Heatmap()
        row.addWidget(wrap_panel(self.top_games_chart), 1)
        row.addWidget(wrap_panel(self.top_keys_chart), 1)
        self.content_layout.addLayout(row)
        self.content_layout.addWidget(wrap_panel(self.heatmap))

    def _build_tables(self) -> None:
        games_label = QLabel("Game Summary")
        games_label.setProperty("title", True)
        self.games_table = QTableWidget(0, 5)
        self.games_table.setHorizontalHeaderLabels(["Game", "Playtime", "Keys", "Mouse", "Inputs / Hour"])
        self.games_table.setMinimumHeight(190)
        self.games_table.verticalHeader().setVisible(False)
        self.games_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        history_label = QLabel("Session History")
        history_label.setProperty("title", True)
        self.recent_table = QTableWidget(0, 6)
        self.recent_table.setHorizontalHeaderLabels(["Game", "Started", "Ended", "Duration", "Keys", "Mouse"])
        self.recent_table.setMinimumHeight(420)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.content_layout.addWidget(games_label)
        self.content_layout.addWidget(self.games_table)
        self.content_layout.addWidget(history_label)
        self.content_layout.addWidget(self.recent_table)

    def set_active_game(self, game_name: str | None, started_at: datetime | None = None) -> None:
        self._session_started_at = started_at
        if game_name:
            self.current_game.setText(game_name)
            self.subtitle.setText("Tracking session is active")
        else:
            self.current_game.setText("No active game")
            self.subtitle.setText("Waiting for a supported game")
            self.session_keys.set_value("0")
            self.session_mouse.set_value("0")
            self.session_duration.set_value("0m")

    def update_session_counters(self, key_count: int, mouse_count: int) -> None:
        self.session_keys.set_value(compact_number(key_count))
        self.session_mouse.set_value(compact_number(mouse_count))

    def refresh_session_duration(self) -> None:
        if not self._session_started_at:
            self.session_duration.set_value("0m")
            return
        elapsed = int((datetime.utcnow() - self._session_started_at).total_seconds())
        self.session_duration.set_value(format_duration(elapsed))

    def refresh_dashboard(self) -> None:
        summary = self.repository.lifetime_summary()
        self.playtime.set_value(format_duration(int(summary["playtime_seconds"])))
        self.keyboard.set_value(compact_number(int(summary["keyboard_presses"])))
        self.mouse.set_value(compact_number(int(summary["mouse_inputs"])))
        self.games.set_value(compact_number(int(summary["games_tracked"])))

        games = self.repository.top_games()
        self.top_games_chart.set_data(
            [(row["name"], int(row["playtime_seconds"])) for row in games[:7]]
        )
        top_keys = self.repository.top_keys()
        self.top_keys_chart.set_data(top_keys)
        self.heatmap.set_keys(top_keys)
        self._fill_games_table(games)
        self._fill_recent_table(self.repository.recent_sessions(limit=50))

    def _fill_games_table(self, games: list[dict[str, object]]) -> None:
        self.games_table.setRowCount(len(games))
        for row_index, row in enumerate(games):
            seconds = int(row["playtime_seconds"])
            inputs = int(row["keyboard_presses"]) + int(row["mouse_inputs"])
            inputs_per_hour = int(inputs / (seconds / 3600)) if seconds else 0
            values = [
                str(row["name"]),
                format_duration(seconds),
                compact_number(int(row["keyboard_presses"])),
                compact_number(int(row["mouse_inputs"])),
                compact_number(inputs_per_hour),
            ]
            for col, value in enumerate(values):
                self.games_table.setItem(row_index, col, QTableWidgetItem(value))
        self.games_table.resizeColumnsToContents()

    def _fill_recent_table(self, sessions: list[dict[str, object]]) -> None:
        self.recent_table.setRowCount(len(sessions))
        for row_index, row in enumerate(sessions):
            started = row["started_at"]
            ended = row["ended_at"]
            started_text = started.strftime("%Y-%m-%d %H:%M") if hasattr(started, "strftime") else "-"
            ended_text = ended.strftime("%Y-%m-%d %H:%M") if hasattr(ended, "strftime") else "Active"
            duration_seconds = int(row["duration_seconds"])
            if ended is None and hasattr(started, "strftime"):
                duration_seconds = max(0, int((datetime.utcnow() - started).total_seconds()))
            values = [
                str(row["game"]),
                started_text,
                ended_text,
                format_duration(duration_seconds),
                compact_number(int(row["keyboard_presses"])),
                compact_number(int(row["mouse_inputs"])),
            ]
            for col, value in enumerate(values):
                self.recent_table.setItem(row_index, col, QTableWidgetItem(value))
        self.recent_table.resizeColumnsToContents()

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()


def wrap_panel(widget: QWidget) -> QFrame:
    frame = QFrame()
    frame.setProperty("panel", True)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(widget)
    return frame

from __future__ import annotations

import psutil
from PySide6.QtCore import QObject, QTimer, Signal

from game_input_tracker.core.game_catalog import GameCandidate, identify_game


class ProcessMonitor(QObject):
    game_started = Signal(object)
    game_stopped = Signal(object)
    scan_completed = Signal()

    def __init__(self, poll_interval_ms: int = 2500) -> None:
        super().__init__()
        self._timer = QTimer(self)
        self._timer.setInterval(poll_interval_ms)
        self._timer.timeout.connect(self.scan)
        self._active: GameCandidate | None = None
        self._custom_games: dict[str, str] = {}

    @property
    def active_game(self) -> GameCandidate | None:
        return self._active

    def set_custom_games(self, custom_games: dict[str, str]) -> None:
        self._custom_games = custom_games

    def start(self) -> None:
        self.scan()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def scan(self) -> None:
        active_pid = self._active.process_id if self._active else None
        seen_active = False
        candidates: list[GameCandidate] = []

        for process in psutil.process_iter(["pid", "name", "exe"]):
            try:
                info = process.info
                pid = int(info.get("pid") or 0)
                if pid == active_pid:
                    seen_active = True
                candidate = identify_game(
                    info.get("name"),
                    pid,
                    info.get("exe"),
                    self._custom_games,
                )
                if candidate:
                    candidates.append(candidate)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if self._active and not seen_active:
            stopped = self._active
            self._active = None
            self.game_stopped.emit(stopped)

        if self._active is None and candidates:
            self._active = candidates[0]
            self.game_started.emit(self._active)

        self.scan_completed.emit()


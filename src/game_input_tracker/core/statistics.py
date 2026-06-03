from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameMetrics:
    name: str
    playtime_seconds: int
    keyboard_presses: int
    mouse_inputs: int
    sessions: int

    @property
    def inputs_per_hour(self) -> float:
        hours = self.playtime_seconds / 3600
        if hours <= 0:
            return 0.0
        return (self.keyboard_presses + self.mouse_inputs) / hours

    @property
    def average_session_seconds(self) -> float:
        if self.sessions <= 0:
            return 0.0
        return self.playtime_seconds / self.sessions


def build_game_metrics(rows: list[dict[str, object]]) -> list[GameMetrics]:
    return [
        GameMetrics(
            name=str(row["name"]),
            playtime_seconds=int(row["playtime_seconds"]),
            keyboard_presses=int(row["keyboard_presses"]),
            mouse_inputs=int(row["mouse_inputs"]),
            sessions=int(row["sessions"]),
        )
        for row in rows
    ]


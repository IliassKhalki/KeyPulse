from game_input_tracker.core.statistics import GameMetrics, build_game_metrics
from game_input_tracker.core.formatting import compact_number, format_duration
from game_input_tracker.core.input_tracker import normalize_button


def test_format_duration() -> None:
    assert format_duration(0) == "0m"
    assert format_duration(65) == "1m"
    assert format_duration(3660) == "1h 1m"


def test_compact_number() -> None:
    assert compact_number(999) == "999"
    assert compact_number(1200) == "1.2K"
    assert compact_number(1_000_000) == "1M"


def test_mouse_names() -> None:
    class Button:
        def __str__(self) -> str:
            return "Button.left"

    assert normalize_button(Button()) == "Left Click"


def test_game_metrics_derived_values() -> None:
    metrics = GameMetrics(
        name="Warframe",
        playtime_seconds=7200,
        keyboard_presses=1800,
        mouse_inputs=600,
        sessions=4,
    )

    assert metrics.inputs_per_hour == 1200
    assert metrics.average_session_seconds == 1800


def test_game_metrics_zero_values() -> None:
    metrics = GameMetrics(
        name="Idle",
        playtime_seconds=0,
        keyboard_presses=10,
        mouse_inputs=5,
        sessions=0,
    )

    assert metrics.inputs_per_hour == 0.0
    assert metrics.average_session_seconds == 0.0


def test_build_game_metrics_converts_repository_rows() -> None:
    rows = [
        {
            "name": "Valorant",
            "playtime_seconds": "3600",
            "keyboard_presses": "2400",
            "mouse_inputs": "600",
            "sessions": "3",
        }
    ]

    assert build_game_metrics(rows) == [
        GameMetrics(
            name="Valorant",
            playtime_seconds=3600,
            keyboard_presses=2400,
            mouse_inputs=600,
            sessions=3,
        )
    ]

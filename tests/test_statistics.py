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


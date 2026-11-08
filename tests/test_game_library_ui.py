import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from game_input_tracker.core.game_library import normalize_path
from game_input_tracker.data.database import (
    create_session_factory, create_sqlite_engine, initialize_database,
)
from game_input_tracker.data.repository import TrackerRepository
from game_input_tracker.ui.game_library import GameLibraryDialog


@pytest.fixture
def repository(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "test.sqlite3")
    initialize_database(engine)
    yield TrackerRepository(create_session_factory(engine))
    engine.dispose()


def test_manual_game_saved_removed_and_cancelled(repository, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr("game_input_tracker.ui.game_library.discover_installed_games", lambda: [])
    monkeypatch.setattr(
        "game_input_tracker.ui.game_library.QFileDialog.getOpenFileName",
        lambda *args: ("D:/Games/An Unknown Game/Game.exe", ""),
    )
    monkeypatch.setattr(
        "game_input_tracker.ui.game_library.QInputDialog.getText",
        lambda *args, **kwargs: ("An Unknown Game", True),
    )
    dialog = GameLibraryDialog(repository)
    dialog.add_game()
    assert repository.custom_game_paths() == {}
    dialog.save()
    expected = {normalize_path("D:/Games/An Unknown Game/Game.exe"): "An Unknown Game"}
    assert repository.custom_game_paths() == expected
    cancelled = GameLibraryDialog(repository)
    cancelled.custom.setCurrentRow(0)
    cancelled.remove_game()
    cancelled.reject()
    assert repository.custom_game_paths() == expected
    reopened = GameLibraryDialog(repository)
    reopened.custom.setCurrentRow(0)
    reopened.remove_game()
    reopened.save()
    assert repository.custom_game_paths() == {}
    for widget in (dialog, cancelled, reopened):
        widget.close()
    app.processEvents()


@pytest.mark.parametrize("raw", ["garbage", "[]", '{"x": 3}', "null"])
def test_invalid_saved_paths_do_not_break_startup(repository, raw) -> None:
    repository.set_setting("custom_game_paths", raw)
    assert repository.custom_game_paths() == {}

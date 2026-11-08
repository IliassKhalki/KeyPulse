import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from game_input_tracker.core.game_catalog import identify_game
from game_input_tracker.core.game_library import (
    InstalledGame, discover_installed_games, installed_game_name, normalize_path,
)
from game_input_tracker.core.process_monitor import ProcessMonitor


def test_discovers_secondary_steam_library_and_epic(tmp_path: Path) -> None:
    steam, secondary, epic = (tmp_path / name for name in ("Steam", "OtherDrive", "Epic"))
    (steam / "steamapps").mkdir(parents=True)
    (secondary / "steamapps/common/Unknown Game").mkdir(parents=True)
    epic.mkdir()
    epic_game = tmp_path / "Epic Game"
    epic_game.mkdir()
    library_path = str(secondary).replace("\\", "\\\\")
    (steam / "steamapps/libraryfolders.vdf").write_text(
        f'"libraryfolders" {{ "1" {{ "path" "{library_path}" }} }}', encoding="utf-8"
    )
    (secondary / "steamapps/appmanifest_123.acf").write_text(
        '"AppState" { "appid" "123" "name" "Unknown Game" "installdir" "Unknown Game" }',
        encoding="utf-8",
    )
    (epic / "game.item").write_text(json.dumps({
        "DisplayName": "Epic Game", "InstallLocation": str(epic_game),
        "AppCategories": ["games"],
    }), encoding="utf-8")
    (epic / "broken.item").write_text("{broken", encoding="utf-8")
    (epic / "invalid.item").write_text("[]", encoding="utf-8")
    games = discover_installed_games([steam], epic)
    assert {game.name for game in games} == {"Unknown Game", "Epic Game"}
    assert installed_game_name(str(epic_game / "Binaries/Win64/Game.exe"), games) == "Epic Game"


@pytest.mark.parametrize("folder", ["..", r"..\..", "C:/", "."])
def test_rejects_invalid_steam_directory(tmp_path: Path, folder: str) -> None:
    apps = tmp_path / "steamapps"
    (apps / "common").mkdir(parents=True)
    escaped = folder.replace("\\", "\\\\")
    (apps / "appmanifest_1.acf").write_text(
        f'"name" "Invalid" "installdir" "{escaped}"', encoding="utf-8"
    )
    assert discover_installed_games([tmp_path], tmp_path / "missing") == []


@pytest.mark.parametrize("relative", [
    "CrashReportClient.exe", "EasyAntiCheat.exe", "Launcher.exe",
    "_CommonRedist/runtime.exe", "Game.exe.backup",
])
def test_ignores_helpers(relative: str) -> None:
    assert installed_game_name(
        "D:/Games/Example/" + relative, [InstalledGame("Example", "D:/Games/Example")]
    ) is None


def test_matching_is_case_insensitive_and_requires_directory_boundary() -> None:
    games = [InstalledGame("Example", "D:/Games/Example")]
    assert installed_game_name(r"d:\GAMES\EXAMPLE\bin\game.EXE", games) == "Example"
    assert installed_game_name("D:/Games/ExampleOther/Game.exe", games) is None
    assert installed_game_name("D:/Other/Game.exe", games) is None


@pytest.mark.parametrize("extra", [
    {"bIsIncompleteInstall": True}, {"AppCategories": None},
    {"AppCategories": ["applications"]}, {"DisplayName": ""},
])
def test_skips_incomplete_or_non_game_epic_manifests(tmp_path: Path, extra: dict) -> None:
    data = {
        "DisplayName": "Example", "InstallLocation": str(tmp_path), "AppCategories": ["games"],
        **extra,
    }
    (tmp_path / "game.item").write_text(json.dumps(data), encoding="utf-8")
    assert discover_installed_games([], tmp_path) == []


def test_manual_path_overrides_automatic_name_and_supports_runtime() -> None:
    path = r"D:\My Game\python.exe"
    candidate = identify_game("python.exe", 123, path, custom_paths={normalize_path(path): "My Game"})
    assert candidate is not None and candidate.name == "My Game"
    assert identify_game("python.exe", 123, r"C:\Python\python.exe") is None


def test_same_executable_name_in_different_games_has_separate_identity() -> None:
    games = [InstalledGame("First", "D:/First"), InstalledGame("Second", "D:/Second")]
    first = identify_game("Game.exe", 1, "D:/First/Game.exe", installed_games=games)
    second = identify_game("Game.exe", 2, "D:/Second/Game.exe", installed_games=games)
    assert first is not None and second is not None
    assert (first.name, second.name) == ("First", "Second")
    assert first.executable != second.executable


def test_legacy_catalog_still_works_without_executable_path() -> None:
    game = identify_game("CS2.EXE", 12, None)
    assert game is not None and game.name == "Counter-Strike 2"
    assert identify_game("unknown.exe", 13, None) is None


def test_monitor_starts_and_stops_discovered_game(monkeypatch) -> None:
    monitor = ProcessMonitor()
    monitor._installed_games = [InstalledGame("Example", "D:/Example")]
    processes = [
        SimpleNamespace(info={"pid": 122, "name": "Launcher.exe", "exe": "D:/Example/Launcher.exe"}),
        SimpleNamespace(info={"pid": 123, "name": "Game.exe", "exe": "D:/Example/Game.exe"}),
    ]
    monkeypatch.setattr("game_input_tracker.core.process_monitor.psutil.process_iter", lambda _: processes)
    started, stopped = [], []
    monitor.game_started.connect(started.append)
    monitor.game_stopped.connect(stopped.append)
    monitor.scan()
    monitor.scan()
    assert len(started) == 1 and monitor.active_game.name == "Example"
    processes.clear()
    monitor.scan()
    assert len(stopped) == 1 and monitor.active_game is None

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath


def normalize_path(value: str) -> str:
    return str(PureWindowsPath(value)).lower()


@dataclass(frozen=True)
class InstalledGame:
    name: str
    directory: str


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return ""


def _vdf_values(text: str) -> dict[str, str]:
    # Only string pairs are needed from Steam's local library and app manifests.
    return {
        key.lower(): value.replace("\\\\", "\\").replace('\\"', '"')
        for key, value in re.findall(r'"([^"\\]+)"\s+"((?:\\.|[^"\\])*)"', text)
    }


def steam_roots() -> list[Path]:
    roots = [Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam"]
    if os.name == "nt":
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                roots.append(Path(winreg.QueryValueEx(key, "SteamPath")[0]))
        except OSError:
            pass
    return roots


def discover_installed_games(
    roots: list[Path] | None = None, epic_manifests: Path | None = None
) -> list[InstalledGame]:
    libraries: set[Path] = set()
    for root in steam_roots() if roots is None else roots:
        libraries.add(root)
        text = _read_text(root / "steamapps" / "libraryfolders.vdf")
        for value in re.findall(r'"path"\s+"((?:\\.|[^"\\])*)"', text, re.IGNORECASE):
            libraries.add(Path(value.replace("\\\\", "\\")))

    games: dict[str, InstalledGame] = {}
    for library in sorted(libraries):
        try:
            manifests = list((library / "steamapps").glob("appmanifest_*.acf"))
        except OSError:
            continue
        for manifest in manifests:
            values = _vdf_values(_read_text(manifest))
            name, folder = values.get("name", ""), values.get("installdir", "")
            if not name or not folder or values.get("appid") == "228980":
                continue
            # A corrupt manifest must not make an entire drive a game directory.
            relative = PureWindowsPath(folder)
            if not relative.parts or relative.root or relative.drive or ".." in relative.parts:
                continue
            directory = library / "steamapps" / "common" / Path(*relative.parts)
            if directory.is_dir():
                games[normalize_path(str(directory))] = InstalledGame(name, str(directory))

    if epic_manifests is None:
        epic_manifests = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / (
            "Epic/EpicGamesLauncher/Data/Manifests"
        )
    try:
        manifests = list(epic_manifests.glob("*.item"))
    except OSError:
        manifests = []
    for manifest in manifests:
        try:
            data = json.loads(_read_text(manifest))
        except ValueError:
            continue
        if not isinstance(data, dict) or data.get("bIsIncompleteInstall"):
            continue
        name, folder = data.get("DisplayName"), data.get("InstallLocation")
        if not isinstance(name, str) or not name.strip() or not isinstance(folder, str) or not folder:
            continue
        categories = data.get("AppCategories")
        if not isinstance(categories, list) or "games" not in categories:
            continue
        directory = Path(folder)
        if directory.is_absolute() and directory != directory.parent and directory.is_dir():
            games[normalize_path(folder)] = InstalledGame(name, folder)
    return sorted(games.values(), key=lambda game: game.name.casefold())


HELPER_MARKERS = (
    "crash", "reporter", "unins", "setup", "install", "updater", "launcher",
    "anticheat", "anti-cheat", "easyanticheat", "battleye", "beservice",
    "cef", "webhelper", "overlay", "redist", "dxwebsetup",
)
HELPER_DIRECTORIES = {"_commonredist", "redist", "redistributables", "installer", "__support"}


def installed_game_name(path: str, games: list[InstalledGame]) -> str | None:
    executable = PureWindowsPath(normalize_path(path))
    if executable.suffix != ".exe" or any(word in executable.name for word in HELPER_MARKERS):
        return None
    # Prefer the most specific directory if installations happen to be nested.
    for game in sorted(games, key=lambda game: len(game.directory), reverse=True):
        try:
            relative = executable.relative_to(PureWindowsPath(normalize_path(game.directory)))
        except ValueError:
            continue
        if not any(part in HELPER_DIRECTORIES for part in relative.parts[:-1]):
            return game.name
    return None

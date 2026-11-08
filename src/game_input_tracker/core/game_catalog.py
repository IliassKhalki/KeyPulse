from __future__ import annotations

from dataclasses import dataclass

from game_input_tracker.core.game_library import InstalledGame, installed_game_name, normalize_path


@dataclass(frozen=True)
class GameCandidate:
    name: str
    executable: str
    process_id: int
    path: str | None = None


KNOWN_GAMES: dict[str, str] = {
    "dofus.exe": "Dofus",
    "dofus retro.exe": "Dofus Retro",
    "leagueclientux.exe": "League of Legends",
    "league of legends.exe": "League of Legends",
    "valorant-win64-shipping.exe": "Valorant",
    "cs2.exe": "Counter-Strike 2",
    "javaw.exe": "Minecraft",
    "minecraftlauncher.exe": "Minecraft",
    "gta5.exe": "Grand Theft Auto V",
    "wow.exe": "World of Warcraft",
    "wowclassic.exe": "World of Warcraft Classic",
    "fortniteclient-win64-shipping.exe": "Fortnite",
    "eldenring.exe": "Elden Ring",
    "r5apex.exe": "Apex Legends",
    "overwatch.exe": "Overwatch",
    "destiny2.exe": "Destiny 2",
    "warframe.exe": "Warframe",
    "warframe.x64.exe": "Warframe",
}

IGNORED_PROCESS_NAMES = {
    "applicationframehost.exe",
    "audiodg.exe",
    "chrome.exe",
    "codex.exe",
    "conhost.exe",
    "dwm.exe",
    "explorer.exe",
    "gameinputsvc.exe",
    "msedge.exe",
    "nvidia container.exe",
    "powershell.exe",
    "python.exe",
    "pythonw.exe",
    "searchhost.exe",
    "steam.exe",
    "system",
    "taskhostw.exe",
    "windowsterminal.exe",
    "discord.exe",
    "epicgameslauncher.exe",
    "epicwebhelper.exe",
    "riotclientservices.exe",
    "battle.net.exe",
    "ubisoftconnect.exe",
}


def normalize_executable(name: str | None) -> str:
    return (name or "").strip().lower()


def identify_game(
    process_name: str | None,
    pid: int,
    executable_path: str | None,
    custom_games: dict[str, str] | None = None,
    installed_games: list[InstalledGame] | None = None,
    custom_paths: dict[str, str] | None = None,
) -> GameCandidate | None:
    executable = normalize_executable(process_name)
    # An explicit path also supports games using a shared runtime executable.
    if executable_path and custom_paths:
        path = normalize_path(executable_path)
        if path in custom_paths:
            return GameCandidate(custom_paths[path], path, pid, executable_path)
    if not executable or executable in IGNORED_PROCESS_NAMES:
        return None

    catalog = dict(KNOWN_GAMES)
    if custom_games:
        catalog.update({normalize_executable(k): v for k, v in custom_games.items()})

    if executable in catalog:
        return GameCandidate(catalog[executable], executable, pid, executable_path)

    if executable_path and installed_games:
        name = installed_game_name(executable_path, installed_games)
        if name:
            # Full paths keep unrelated games named Game.exe from sharing statistics.
            return GameCandidate(name, normalize_path(executable_path), pid, executable_path)

    return None

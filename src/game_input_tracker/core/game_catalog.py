from __future__ import annotations

from dataclasses import dataclass


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
}

IGNORED_PROCESS_NAMES = {
    "applicationframehost.exe",
    "audiodg.exe",
    "chrome.exe",
    "codex.exe",
    "conhost.exe",
    "discord.exe",
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
}


def normalize_executable(name: str | None) -> str:
    return (name or "").strip().lower()


def identify_game(
    process_name: str | None,
    pid: int,
    executable_path: str | None,
    custom_games: dict[str, str] | None = None,
) -> GameCandidate | None:
    executable = normalize_executable(process_name)
    if not executable or executable in IGNORED_PROCESS_NAMES:
        return None

    catalog = dict(KNOWN_GAMES)
    if custom_games:
        catalog.update({normalize_executable(k): v for k, v in custom_games.items()})

    if executable in catalog:
        return GameCandidate(catalog[executable], executable, pid, executable_path)

    return None

from __future__ import annotations

import asyncio
import os
from datetime import datetime

from game_input_tracker.core.formatting import compact_number, format_duration
from game_input_tracker.core.settings import get_app_paths
from game_input_tracker.data.database import (
    create_session_factory,
    create_sqlite_engine,
    initialize_database,
)
from game_input_tracker.data.repository import TrackerRepository


def _repository() -> TrackerRepository:
    paths = get_app_paths()
    engine = create_sqlite_engine(paths.database_path)
    initialize_database(engine)
    return TrackerRepository(create_session_factory(engine))


def _session_duration(row: dict[str, object]) -> int:
    if row["ended_at"] is None and isinstance(row["started_at"], datetime):
        return max(0, int((datetime.utcnow() - row["started_at"]).total_seconds()))
    return int(row["duration_seconds"] or 0)


def _format_started(value: object) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return "Unknown"


def _limit(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


async def run_bot() -> None:
    try:
        import discord
        from discord import app_commands
    except ImportError as exc:
        raise SystemExit(
            "Discord support is not installed. Run:\n"
            ".\\.venv\\Scripts\\python.exe -m pip install -r requirements-discord.txt"
        ) from exc

    token = os.getenv("KEYPULSE_DISCORD_TOKEN", "").strip()
    if not token:
        raise SystemExit("Set KEYPULSE_DISCORD_TOKEN before starting the KeyPulse Discord bot.")

    repository = _repository()
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @tree.command(name="keypulse_stats", description="Show KeyPulse lifetime stats.")
    async def keypulse_stats(interaction: discord.Interaction) -> None:
        summary = repository.lifetime_summary()
        embed = discord.Embed(
            title="KeyPulse Lifetime Stats",
            color=0x00D1FF,
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name="Playtime",
            value=format_duration(int(summary["playtime_seconds"])),
            inline=True,
        )
        embed.add_field(name="Sessions", value=compact_number(int(summary["sessions"])), inline=True)
        embed.add_field(
            name="Games Tracked",
            value=compact_number(int(summary["games_tracked"])),
            inline=True,
        )
        embed.add_field(
            name="Keyboard Presses",
            value=compact_number(int(summary["keyboard_presses"])),
            inline=True,
        )
        embed.add_field(
            name="Mouse Inputs",
            value=compact_number(int(summary["mouse_inputs"])),
            inline=True,
        )
        embed.add_field(name="Most Played", value=str(summary["most_played_game"]), inline=True)
        embed.add_field(name="Most Used Key", value=str(summary["most_used_key"]), inline=True)
        embed.add_field(name="Most Used Mouse", value=str(summary["most_used_mouse"]), inline=True)
        await interaction.response.send_message(embed=embed)

    @tree.command(name="keypulse_recent", description="Show recent KeyPulse game sessions.")
    @app_commands.describe(limit="How many sessions to show, from 1 to 10.")
    async def keypulse_recent(interaction: discord.Interaction, limit: int = 5) -> None:
        sessions = repository.recent_sessions(limit=_limit(limit, 1, 10))
        if not sessions:
            await interaction.response.send_message("No KeyPulse sessions yet.")
            return

        lines = []
        for row in sessions:
            status = "Active" if row["ended_at"] is None else "Ended"
            lines.append(
                f"**{row['game']}** | {status} | {_format_started(row['started_at'])} | "
                f"{format_duration(_session_duration(row))} | "
                f"{compact_number(int(row['keyboard_presses']))} keys | "
                f"{compact_number(int(row['mouse_inputs']))} mouse"
            )
        await interaction.response.send_message("\n".join(lines))

    @tree.command(name="keypulse_games", description="Show top KeyPulse games by playtime.")
    @app_commands.describe(limit="How many games to show, from 1 to 10.")
    async def keypulse_games(interaction: discord.Interaction, limit: int = 5) -> None:
        games = repository.top_games(limit=_limit(limit, 1, 10))
        if not games:
            await interaction.response.send_message("No tracked games yet.")
            return

        lines = []
        for index, game in enumerate(games, start=1):
            lines.append(
                f"**{index}. {game['name']}** | "
                f"{format_duration(int(game['playtime_seconds']))} | "
                f"{compact_number(int(game['keyboard_presses']))} keys | "
                f"{compact_number(int(game['mouse_inputs']))} mouse | "
                f"{compact_number(int(game['sessions']))} sessions"
            )
        await interaction.response.send_message("\n".join(lines))

    @tree.command(name="keypulse_keys", description="Show the most-used KeyPulse keys.")
    @app_commands.describe(limit="How many keys to show, from 1 to 15.")
    async def keypulse_keys(interaction: discord.Interaction, limit: int = 10) -> None:
        keys = repository.top_keys(limit=_limit(limit, 1, 15))
        if not keys:
            await interaction.response.send_message("No keyboard stats yet.")
            return

        lines = [
            f"**{index}. {key_name}** | {compact_number(count)} presses"
            for index, (key_name, count) in enumerate(keys, start=1)
        ]
        await interaction.response.send_message("\n".join(lines))

    @client.event
    async def on_ready() -> None:
        guild_id = os.getenv("KEYPULSE_DISCORD_GUILD_ID", "").strip()
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            tree.copy_global_to(guild=guild)
            await tree.sync(guild=guild)
        else:
            await tree.sync()
        print(f"KeyPulse Discord bot connected as {client.user}.")

    await client.start(token)


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()

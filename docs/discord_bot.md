# KeyPulse Discord Companion

KeyPulse can run an optional Discord companion bot on the same Windows PC as the desktop app.

The bot reads the local KeyPulse SQLite database and answers Discord slash commands. It does not track keyboard input, store chat messages, or send your raw database anywhere.

## Commands

- `/keypulse_stats` shows lifetime playtime, sessions, games tracked, keyboard presses, mouse inputs, and top inputs.
- `/keypulse_recent` shows recent game sessions.
- `/keypulse_games` shows top games by playtime.
- `/keypulse_keys` shows the most-used keys.

## Setup

1. Create a Discord application in the Discord Developer Portal.
2. Add a bot to that application.
3. Copy the bot token.
4. Invite the bot to your server with the `bot` and `applications.commands` scopes.
5. Install the optional Discord dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-discord.txt
```

6. Store the token locally. Do not paste it into chat or commit it to GitHub:

```powershell
[Environment]::SetEnvironmentVariable("KEYPULSE_DISCORD_TOKEN", "YOUR_TOKEN_HERE", "User")
```

7. Start a new PowerShell window, then run:

```powershell
.\.venv\Scripts\python.exe -m game_input_tracker.discord_bot
```

## Faster Slash Command Registration

Global slash commands can take time to appear. For faster testing, set your Discord server ID:

```powershell
[Environment]::SetEnvironmentVariable("KEYPULSE_DISCORD_GUILD_ID", "YOUR_SERVER_ID", "User")
```

Then restart the bot.

## Important Notes

- The bot must run on the PC where KeyPulse stores its database.
- The desktop app does the tracking. The Discord bot is a read-only companion.
- Keep `KEYPULSE_DISCORD_TOKEN` private. If it leaks, reset the token in Discord immediately.

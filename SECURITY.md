# Security Policy

## Supported Status

KeyPulse is an early desktop analytics project. Security fixes should target the current `master` branch unless a release branch exists.

## What KeyPulse Does

- Runs as a native Windows desktop app.
- Detects known game processes.
- Counts keyboard and mouse inputs only while a tracked game session is active.
- Stores local statistics in SQLite on the user's Windows profile.
- Optionally runs a Discord companion bot that reads local statistics and answers slash commands.

## What KeyPulse Does Not Do

- It does not store typed text.
- It does not store passwords, chat messages, clipboard data, screenshots, or window contents.
- It does not inject into games.
- It does not read game memory.
- It does not inspect network packets.
- It does not upload the local database to KeyPulse servers.

## Secrets

Discord bot tokens, client secrets, OAuth secrets, webhook URLs, and `.env` files must never be committed.

If a Discord token is exposed:

1. Reset the token in the Discord Developer Portal immediately.
2. Stop any running bot process using the old token.
3. Restart the bot with the new token through an environment variable.

## Reporting Issues

For now, report security issues privately to the project maintainer before opening a public GitHub issue.

Include:

- A short description of the issue.
- Steps to reproduce.
- The affected version or commit.
- Whether a secret, local database, or Discord permission is involved.

## Production Checklist

- Use a fresh Discord bot token stored outside Git.
- Keep `.env` files ignored.
- Use least-privilege Discord permissions.
- Use private slash-command responses for personal statistics.
- Code-sign Windows releases before wide distribution.
- Publish a Privacy Policy and Terms of Service before public Discord use.
- Build Linked Roles with a hosted HTTPS OAuth2 verification service, not with local-only desktop state.

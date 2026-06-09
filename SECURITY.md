# Security Policy

## Supported Status

KeyPulse is an early desktop analytics project. Security fixes should target the current `master` branch unless a release branch exists.

## What KeyPulse Does

- Runs as a native Windows desktop app.
- Detects known game processes.
- Counts keyboard and mouse inputs only while a tracked game session is active.
- Stores local statistics in SQLite on the user's Windows profile.

## What KeyPulse Does Not Do

- It does not store typed text.
- It does not store passwords, chat messages, clipboard data, screenshots, or window contents.
- It does not inject into games.
- It does not read game memory.
- It does not inspect network packets.
- It does not upload the local database to KeyPulse servers.

## Secrets

API tokens, client secrets, webhook URLs, and `.env` files must never be committed.

If a secret is exposed:

1. Revoke or rotate the exposed secret immediately.
2. Stop any running process using the old secret.
3. Restart the app with the new secret through an environment variable or secure local store.

## Reporting Issues

For now, report security issues privately to the project maintainer before opening a public GitHub issue.

Include:

- A short description of the issue.
- Steps to reproduce.
- The affected version or commit.
- Whether a secret or local database is involved.

## Production Checklist

- Keep `.env` files ignored.
- Code-sign Windows releases before wide distribution.
- Publish a Privacy Policy and Terms of Service before wide public distribution.

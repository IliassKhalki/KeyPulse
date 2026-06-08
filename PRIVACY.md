# KeyPulse Privacy Policy

Effective date: 2026-06-08

KeyPulse is a Windows desktop analytics tool for gamers. It is designed to measure numerical input statistics without recording what users type.

## Data KeyPulse Collects Locally

KeyPulse may store the following data on the user's computer:

- Game executable names and display names.
- Game session start and end times.
- Session duration.
- Total keyboard press counts.
- Per-key numerical press counts.
- Mouse click and scroll counts.
- Local app settings.

## Data KeyPulse Does Not Collect

KeyPulse does not intentionally collect or store:

- Typed text.
- Passwords.
- Chat messages.
- Clipboard contents.
- Screenshots.
- Window contents.
- Game memory.
- Network traffic.

## Local Storage

KeyPulse stores statistics locally in SQLite under the user's Windows app data directory. The data remains on the user's computer unless the user chooses to share it.

## Discord Companion Bot

The optional Discord companion bot reads the local KeyPulse SQLite database on the same computer where it runs. It can display summarized statistics through Discord slash commands.

Slash-command responses are private by default when Discord supports ephemeral responses. Server administrators and Discord may still process interaction metadata according to Discord's own policies.

KeyPulse does not require users to paste Discord bot tokens into source code. Tokens should be stored in local environment variables.

## Linked Roles

Discord Linked Roles require a hosted verification flow. If KeyPulse adds Linked Roles support, the verification service will request only the Discord OAuth2 permissions required to connect a user's KeyPulse stats to Discord role metadata.

## Data Sharing

KeyPulse does not sell user data.

KeyPulse does not upload the local statistics database to a KeyPulse cloud service in the current version.

## Data Deletion

Users can delete local KeyPulse data by removing the local SQLite database from the KeyPulse app data directory. If a future hosted Linked Roles service is added, that service must provide a way to unlink Discord accounts and delete hosted verification records.

## Contact

For privacy questions, contact the project maintainer through the GitHub repository.

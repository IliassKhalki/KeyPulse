# Discord Linked Roles Plan

KeyPulse's current Discord companion is a local bot. It can answer slash commands from the local SQLite database, but it is not enough for Discord Linked Roles by itself.

Discord Linked Roles require:

- A public HTTPS Linked Roles Verification URL.
- A Discord OAuth2 flow.
- The `role_connections.write` scope.
- A hosted service that can update a Discord user's role connection metadata.
- A registered application role connection metadata schema.

## Suggested Metadata

Discord allows up to 5 metadata records per application. A KeyPulse Linked Roles version should use a small, privacy-conscious schema:

- `verified_keypulse_user`: boolean, true after successful verification.
- `games_tracked`: integer, total games tracked.
- `sessions`: integer, total completed sessions.
- `playtime_hours`: integer, total tracked playtime in hours.
- `last_session_at`: datetime, last completed session timestamp.

Avoid publishing raw per-key counts as Linked Roles metadata. Per-key data is more personal and belongs in private slash-command responses unless the user explicitly opts in.

## URLs Needed In Discord Developer Portal

Use the public GitHub file URLs immediately:

- Terms of Service URL: `https://github.com/IliassKhalki/KeyPulse/blob/master/TERMS.md`
- Privacy Policy URL: `https://github.com/IliassKhalki/KeyPulse/blob/master/PRIVACY.md`

Later, GitHub Pages can provide cleaner URLs if it is enabled for the repository.

The Linked Roles Verification URL must point to a hosted verification service, for example:

- `https://keypulse.example.com/linked-role`

Do not use a local desktop URL for production Linked Roles. Discord users outside the developer machine will not be able to access it.

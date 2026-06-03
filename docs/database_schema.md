# KeyPulse Database Schema

SQLite database location:

```text
%LOCALAPPDATA%\KeyPulse\KeyPulse\keypulse.sqlite3
```

The exact path is resolved through `platformdirs.user_data_dir()`.

## Tables

### games

Stores one row per executable.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | Primary key |
| name | string | Display name |
| executable | string | Unique normalized executable name |
| path | string | Last known executable path |
| first_seen_at | datetime | First detection time |
| last_seen_at | datetime | Most recent detection time |

### sessions

Stores one row per game session.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | Primary key |
| game_id | integer | Foreign key to games |
| started_at | datetime | Session start |
| ended_at | datetime | Session end |
| duration_seconds | integer | Final duration |
| keyboard_presses | integer | Session keyboard total |
| mouse_inputs | integer | Session mouse total |

### keyboard_stats

Stores per-session key counters.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | Primary key |
| session_id | integer | Foreign key to sessions |
| game_id | integer | Foreign key to games |
| key_name | string | Normalized key name |
| press_count | integer | Numeric count |

Unique constraint: `(session_id, key_name)`.

### mouse_stats

Stores per-session mouse counters.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | Primary key |
| session_id | integer | Foreign key to sessions |
| game_id | integer | Foreign key to games |
| button_name | string | Left Click, Right Click, Middle Click, Scroll Up, Scroll Down |
| input_count | integer | Numeric count |

Unique constraint: `(session_id, button_name)`.

### daily_game_stats

Rollup table for fast long-term historical views.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | Primary key |
| game_id | integer | Foreign key to games |
| day | string | ISO date |
| playtime_seconds | integer | Daily playtime |
| keyboard_presses | integer | Daily keyboard total |
| mouse_inputs | integer | Daily mouse total |

Unique constraint: `(game_id, day)`.

### settings

Simple key/value store for app settings.

| Column | Type | Notes |
| --- | --- | --- |
| key | string | Primary key |
| value | string | Setting value |

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session, sessionmaker

from game_input_tracker.core.game_catalog import GameCandidate
from game_input_tracker.data.models import DailyGameStat, Game, KeyboardStat, MouseStat, Setting, TrackingSession


class TrackerRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_setting(self, key: str, default: str = "") -> str:
        with self._session_factory() as session:
            value = session.get(Setting, key)
            return value.value if value else default

    def set_setting(self, key: str, value: str) -> None:
        with self._session_factory() as session:
            setting = session.get(Setting, key)
            if setting:
                setting.value = value
            else:
                session.add(Setting(key=key, value=value))
            session.commit()

    def custom_games(self) -> dict[str, str]:
        raw = self.get_setting("custom_games", "")
        games: dict[str, str] = {}
        for line in raw.splitlines():
            if "=" in line:
                executable, name = line.split("=", 1)
                games[executable.strip().lower()] = name.strip()
        return games

    def ensure_game(self, candidate: GameCandidate) -> Game:
        now = datetime.utcnow()
        with self._session_factory() as session:
            game = session.scalar(select(Game).where(Game.executable == candidate.executable))
            if game is None:
                game = Game(
                    name=candidate.name,
                    executable=candidate.executable,
                    path=candidate.path,
                    first_seen_at=now,
                    last_seen_at=now,
                )
                session.add(game)
            else:
                game.name = candidate.name
                game.path = candidate.path or game.path
                game.last_seen_at = now
            session.commit()
            return game

    def start_session(self, candidate: GameCandidate) -> TrackingSession:
        game = self.ensure_game(candidate)
        with self._session_factory() as session:
            tracking_session = TrackingSession(game_id=game.id, started_at=datetime.utcnow())
            session.add(tracking_session)
            session.commit()
            tracking_session.game = game
            return tracking_session

    def flush_inputs(
        self,
        session_id: int,
        game_id: int,
        key_counts: Mapping[str, int],
        mouse_counts: Mapping[str, int],
    ) -> None:
        if not key_counts and not mouse_counts:
            return
        with self._session_factory() as session:
            total_keys = sum(key_counts.values())
            total_mouse = sum(mouse_counts.values())
            session.execute(
                insert(TrackingSession)
                .values(id=session_id, game_id=game_id, started_at=datetime.utcnow())
                .on_conflict_do_update(
                    index_elements=[TrackingSession.id],
                    set_={
                        "keyboard_presses": TrackingSession.keyboard_presses + total_keys,
                        "mouse_inputs": TrackingSession.mouse_inputs + total_mouse,
                    },
                )
            )
            for key_name, count in key_counts.items():
                session.execute(
                    insert(KeyboardStat)
                    .values(
                        session_id=session_id,
                        game_id=game_id,
                        key_name=key_name,
                        press_count=count,
                    )
                    .on_conflict_do_update(
                        index_elements=["session_id", "key_name"],
                        set_={"press_count": KeyboardStat.press_count + count},
                    )
                )
            for button_name, count in mouse_counts.items():
                session.execute(
                    insert(MouseStat)
                    .values(
                        session_id=session_id,
                        game_id=game_id,
                        button_name=button_name,
                        input_count=count,
                    )
                    .on_conflict_do_update(
                        index_elements=["session_id", "button_name"],
                        set_={"input_count": MouseStat.input_count + count},
                    )
                )
            session.commit()

    def end_session(self, session_id: int) -> None:
        ended_at = datetime.utcnow()
        with self._session_factory() as session:
            tracking_session = session.get(TrackingSession, session_id)
            if not tracking_session or tracking_session.ended_at:
                return
            tracking_session.ended_at = ended_at
            tracking_session.duration_seconds = max(
                0, int((ended_at - tracking_session.started_at).total_seconds())
            )
            day = tracking_session.started_at.date().isoformat()
            session.execute(
                insert(DailyGameStat)
                .values(
                    game_id=tracking_session.game_id,
                    day=day,
                    playtime_seconds=tracking_session.duration_seconds,
                    keyboard_presses=tracking_session.keyboard_presses,
                    mouse_inputs=tracking_session.mouse_inputs,
                )
                .on_conflict_do_update(
                    index_elements=["game_id", "day"],
                    set_={
                        "playtime_seconds": DailyGameStat.playtime_seconds
                        + tracking_session.duration_seconds,
                        "keyboard_presses": DailyGameStat.keyboard_presses
                        + tracking_session.keyboard_presses,
                        "mouse_inputs": DailyGameStat.mouse_inputs + tracking_session.mouse_inputs,
                    },
                )
            )
            session.commit()

    def lifetime_summary(self) -> dict[str, object]:
        with self._session_factory() as session:
            totals = session.execute(
                select(
                    func.coalesce(func.sum(TrackingSession.duration_seconds), 0),
                    func.coalesce(func.sum(TrackingSession.keyboard_presses), 0),
                    func.coalesce(func.sum(TrackingSession.mouse_inputs), 0),
                    func.count(TrackingSession.id),
                )
            ).one()
            games_tracked = session.scalar(select(func.count(Game.id))) or 0
            most_played = session.execute(
                select(Game.name, func.sum(TrackingSession.duration_seconds).label("seconds"))
                .join(TrackingSession, TrackingSession.game_id == Game.id)
                .group_by(Game.id)
                .order_by(func.sum(TrackingSession.duration_seconds).desc())
                .limit(1)
            ).first()
            most_key = session.execute(
                select(KeyboardStat.key_name, func.sum(KeyboardStat.press_count).label("count"))
                .group_by(KeyboardStat.key_name)
                .order_by(func.sum(KeyboardStat.press_count).desc())
                .limit(1)
            ).first()
            most_mouse = session.execute(
                select(MouseStat.button_name, func.sum(MouseStat.input_count).label("count"))
                .group_by(MouseStat.button_name)
                .order_by(func.sum(MouseStat.input_count).desc())
                .limit(1)
            ).first()
            return {
                "playtime_seconds": int(totals[0]),
                "keyboard_presses": int(totals[1]),
                "mouse_inputs": int(totals[2]),
                "sessions": int(totals[3]),
                "games_tracked": int(games_tracked),
                "most_played_game": most_played[0] if most_played else "None",
                "most_used_key": most_key[0] if most_key else "None",
                "most_used_mouse": most_mouse[0] if most_mouse else "None",
            }

    def top_games(self, limit: int = 8) -> list[dict[str, object]]:
        with self._session_factory() as session:
            rows = session.execute(
                select(
                    Game.name,
                    func.coalesce(func.sum(TrackingSession.duration_seconds), 0).label("playtime"),
                    func.coalesce(func.sum(TrackingSession.keyboard_presses), 0).label("keys"),
                    func.coalesce(func.sum(TrackingSession.mouse_inputs), 0).label("mouse"),
                    func.count(TrackingSession.id).label("sessions"),
                )
                .join(TrackingSession, TrackingSession.game_id == Game.id)
                .group_by(Game.id)
                .order_by(func.sum(TrackingSession.duration_seconds).desc())
                .limit(limit)
            ).all()
            return [
                {
                    "name": row.name,
                    "playtime_seconds": int(row.playtime),
                    "keyboard_presses": int(row.keys),
                    "mouse_inputs": int(row.mouse),
                    "sessions": int(row.sessions),
                }
                for row in rows
            ]

    def top_keys(self, limit: int = 12, game_id: int | None = None) -> list[tuple[str, int]]:
        with self._session_factory() as session:
            statement = select(
                KeyboardStat.key_name,
                func.coalesce(func.sum(KeyboardStat.press_count), 0).label("count"),
            ).group_by(KeyboardStat.key_name)
            if game_id is not None:
                statement = statement.where(KeyboardStat.game_id == game_id)
            rows = session.execute(
                statement.order_by(func.sum(KeyboardStat.press_count).desc()).limit(limit)
            ).all()
            return [(row.key_name, int(row.count)) for row in rows]

    def recent_sessions(self, limit: int = 8) -> list[dict[str, object]]:
        with self._session_factory() as session:
            rows = session.execute(
                select(TrackingSession, Game.name)
                .join(Game, Game.id == TrackingSession.game_id)
                .order_by(TrackingSession.started_at.desc())
                .limit(limit)
            ).all()
            return [
                {
                    "game": game_name,
                    "started_at": tracking_session.started_at,
                    "ended_at": tracking_session.ended_at,
                    "duration_seconds": tracking_session.duration_seconds,
                    "keyboard_presses": tracking_session.keyboard_presses,
                    "mouse_inputs": tracking_session.mouse_inputs,
                }
                for tracking_session, game_name in rows
            ]

    def game_summaries(self) -> list[dict[str, object]]:
        return self.top_games(limit=1000)


from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    executable: Mapped[str] = mapped_column(String(260), nullable=False, unique=True, index=True)
    path: Mapped[str | None] = mapped_column(String(520), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    sessions: Mapped[list["TrackingSession"]] = relationship(back_populates="game")


class TrackingSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    keyboard_presses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mouse_inputs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    game: Mapped[Game] = relationship(back_populates="sessions")
    key_stats: Mapped[list["KeyboardStat"]] = relationship(back_populates="session")
    mouse_stats: Mapped[list["MouseStat"]] = relationship(back_populates="session")


class KeyboardStat(Base):
    __tablename__ = "keyboard_stats"
    __table_args__ = (
        UniqueConstraint("session_id", "key_name", name="uq_keyboard_session_key"),
        Index("ix_keyboard_game_key", "game_id", "key_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    key_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    press_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped[TrackingSession] = relationship(back_populates="key_stats")


class MouseStat(Base):
    __tablename__ = "mouse_stats"
    __table_args__ = (
        UniqueConstraint("session_id", "button_name", name="uq_mouse_session_button"),
        Index("ix_mouse_game_button", "game_id", "button_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    button_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    input_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped[TrackingSession] = relationship(back_populates="mouse_stats")


class DailyGameStat(Base):
    __tablename__ = "daily_game_stats"
    __table_args__ = (
        UniqueConstraint("game_id", "day", name="uq_daily_game_day"),
        Index("ix_daily_day_game", "day", "game_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    day: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    playtime_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    keyboard_presses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mouse_inputs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(String(1000), nullable=False)

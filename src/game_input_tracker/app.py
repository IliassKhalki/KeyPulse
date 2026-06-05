from __future__ import annotations

import sys
from datetime import datetime
from importlib.resources import files

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QStyle, QSystemTrayIcon

from game_input_tracker.core.controller_tracker import ControllerTracker
from game_input_tracker.core.game_catalog import GameCandidate
from game_input_tracker.core.input_tracker import InputTracker
from game_input_tracker.core.process_monitor import ProcessMonitor
from game_input_tracker.core.settings import get_app_paths
from game_input_tracker.data.database import (
    create_session_factory,
    create_sqlite_engine,
    initialize_database,
)
from game_input_tracker.data.repository import TrackerRepository
from game_input_tracker.ui.main_window import MainWindow
from game_input_tracker.ui.overlay import InputOverlay
from game_input_tracker.ui.splash import SplashScreen
from game_input_tracker.ui.theme import STYLE_SHEET


class AppController:
    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.paths = get_app_paths()
        self.engine = create_sqlite_engine(self.paths.database_path)
        initialize_database(self.engine)
        self.repository = TrackerRepository(create_session_factory(self.engine))

        self.window = MainWindow(self.repository)
        self.icon = load_app_icon()
        self.splash = SplashScreen(self.icon)
        if not self.icon.isNull():
            self.app.setWindowIcon(self.icon)
            self.window.setWindowIcon(self.icon)
        self.window.refresh_requested.connect(self.refresh)
        self.window.startup_toggled.connect(self.set_start_with_windows)
        self.overlay = InputOverlay()
        self.window.overlay_toggled.connect(self.overlay.set_overlay_visible)
        self.controller_tracker = ControllerTracker()
        self.controller_tracker.active_controller_inputs_changed.connect(
            self.overlay.set_controller_inputs
        )

        self.monitor = ProcessMonitor()
        self.monitor.set_custom_games(self.repository.custom_games())
        self.monitor.game_started.connect(self.on_game_started)
        self.monitor.game_stopped.connect(self.on_game_stopped)

        self.input_tracker = InputTracker()
        self.input_tracker.counters_changed.connect(self.window.update_session_counters)
        self.input_tracker.active_inputs_changed.connect(self.overlay.set_active_inputs)
        self.input_tracker.hook_error.connect(self.on_hook_error)

        self.flush_timer = QTimer()
        self.flush_timer.setInterval(5000)
        self.flush_timer.timeout.connect(self.flush_inputs)

        self.dashboard_timer = QTimer()
        self.dashboard_timer.setInterval(10000)
        self.dashboard_timer.timeout.connect(self.refresh)
        self.session_timer = QTimer()
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self.window.refresh_session_duration)

        self.tray = self._create_tray()
        self.active_session_id: int | None = None
        self.active_game_id: int | None = None
        self._shutting_down = False

    def start(self) -> None:
        self.splash.show_centered()
        QTimer.singleShot(6000, self._finish_startup)

    def _finish_startup(self) -> None:
        self.window.startup.blockSignals(True)
        self.window.startup.setChecked(is_start_with_windows_enabled())
        self.window.startup.blockSignals(False)
        self.input_tracker.start_hooks()
        self.controller_tracker.start()
        self.monitor.start()
        self.flush_timer.start()
        self.dashboard_timer.start()
        self.session_timer.start()
        self.refresh()
        self.splash.close()
        self.window.show()
        self.tray.show()

    def shutdown(self) -> None:
        if self._shutting_down:
            return
        self._shutting_down = True
        self.close_active_session()
        self.input_tracker.stop_hooks()
        self.controller_tracker.stop()
        self.monitor.stop()
        self.tray.hide()
        self.overlay.hide()
        self.app.quit()

    def on_game_started(self, candidate: GameCandidate) -> None:
        tracking_session = self.repository.start_session(candidate)
        self.active_session_id = tracking_session.id
        self.active_game_id = tracking_session.game_id
        self.input_tracker.begin_session()
        self.window.set_active_game(candidate.name, datetime.utcnow())
        self.window.refresh_session_duration()
        self.tray.showMessage(
            "KeyPulse",
            f"Tracking started for {candidate.name}",
            QSystemTrayIcon.Information,
            2500,
        )
        self.refresh()

    def on_game_stopped(self, _candidate: GameCandidate) -> None:
        self.close_active_session()
        self.window.set_active_game(None)
        self.overlay.set_active_inputs(set())
        self.refresh()

    def flush_inputs(self) -> None:
        if self.active_session_id is None or self.active_game_id is None:
            return
        key_counts, mouse_counts = self.input_tracker.drain_counts()
        self.repository.flush_inputs(
            self.active_session_id,
            self.active_game_id,
            key_counts,
            mouse_counts,
        )

    def close_active_session(self) -> None:
        if self.active_session_id is None or self.active_game_id is None:
            return
        session_id = self.active_session_id
        game_id = self.active_game_id
        self.active_session_id = None
        self.active_game_id = None
        key_counts, mouse_counts = self.input_tracker.end_session()
        self.repository.flush_inputs(session_id, game_id, key_counts, mouse_counts)
        self.repository.end_session(session_id)

    def refresh(self) -> None:
        self.window.refresh_dashboard()

    def set_start_with_windows(self, enabled: bool) -> None:
        try:
            set_start_with_windows(enabled)
        except OSError as exc:
            QMessageBox.warning(self.window, "Startup setting failed", str(exc))
            self.window.startup.blockSignals(True)
            self.window.startup.setChecked(is_start_with_windows_enabled())
            self.window.startup.blockSignals(False)

    def on_hook_error(self, message: str) -> None:
        QMessageBox.warning(
            self.window,
            "Input hooks unavailable",
            "Keyboard and mouse hooks could not start. Run the app from a normal Windows "
            f"desktop session.\n\n{message}",
        )

    def _create_tray(self) -> QSystemTrayIcon:
        tray = QSystemTrayIcon(self.window)
        tray.setIcon(
            self.icon
            if not self.icon.isNull()
            else self.window.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        )
        menu = QMenu()
        show_action = QAction("Show Dashboard", menu)
        show_action.triggered.connect(self.window.showNormal)
        hide_action = QAction("Hide to Tray", menu)
        hide_action.triggered.connect(self.window.hide)
        quit_action = QAction("Quit Tracking", menu)
        quit_action.triggered.connect(self.shutdown)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        tray.setContextMenu(menu)
        tray.activated.connect(
            lambda reason: self.window.showNormal()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
        return tray


def is_start_with_windows_enabled() -> bool:
    if sys.platform != "win32":
        return False
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        ) as key:
            winreg.QueryValueEx(key, "KeyPulse")
            return True
    except FileNotFoundError:
        return False


def set_start_with_windows(enabled: bool) -> None:
    if sys.platform != "win32":
        return
    import winreg

    command = f'"{sys.executable}" -m game_input_tracker'
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if enabled:
            winreg.SetValueEx(key, "KeyPulse", 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, "KeyPulse")
            except FileNotFoundError:
                pass


def load_app_icon() -> QIcon:
    icon_path = files("game_input_tracker").joinpath("assets/keypulse-icon.png")
    return QIcon(str(icon_path))


def run() -> int:
    QApplication.setApplicationName("KeyPulse")
    QApplication.setOrganizationName("KeyPulse")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(STYLE_SHEET)
    controller = AppController(app)
    app.aboutToQuit.connect(controller.shutdown)
    controller.start()
    return app.exec()

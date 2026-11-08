from __future__ import annotations

from pathlib import PureWindowsPath

from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QInputDialog, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout,
)

from game_input_tracker.core.game_library import discover_installed_games, normalize_path
from game_input_tracker.data.repository import TrackerRepository


class GameLibraryDialog(QDialog):
    def __init__(self, repository: TrackerRepository, parent=None) -> None:
        super().__init__(parent)
        self.repository = repository
        self.paths = repository.custom_game_paths()
        self.setWindowTitle("Game Detection")
        self.resize(650, 520)
        layout = QVBoxLayout(self)
        explanation = QLabel(
            "Steam and Epic games are discovered automatically. For any other game, "
            "add the executable that runs while you play. You can also add an executable "
            "to correct automatic detection. Changes apply when you save."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        layout.addWidget(QLabel("Installed Steam / Epic games"))
        self.installed = QListWidget()
        layout.addWidget(self.installed)
        rescan = QPushButton("Rescan Installed Games")
        rescan.clicked.connect(self.refresh_installed)
        layout.addWidget(rescan)
        layout.addWidget(QLabel("Manually added games"))
        self.custom = QListWidget()
        self.custom.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.custom)
        actions = QHBoxLayout()
        add = QPushButton("Add Game (.exe)")
        add.clicked.connect(self.add_game)
        remove = QPushButton("Remove Selected")
        remove.clicked.connect(self.remove_game)
        actions.addWidget(add)
        actions.addWidget(remove)
        layout.addLayout(actions)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh_installed()
        self.refresh_custom()

    def refresh_installed(self) -> None:
        self.installed.clear()
        games = discover_installed_games()
        for game in games:
            item = QListWidgetItem(game.name)
            item.setToolTip(game.directory)
            self.installed.addItem(item)
        if not games:
            self.installed.addItem("No Steam or Epic installations found. Add games below.")

    def refresh_custom(self) -> None:
        self.custom.clear()
        for path, name in self.paths.items():
            item = QListWidgetItem(f"{name} - {path}")
            item.setToolTip(path)
            self.custom.addItem(item)

    def add_game(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Game Executable", "", "Games (*.exe)")
        if not path:
            return
        name, accepted = QInputDialog.getText(
            self, "Game Name", "Display name:", text=PureWindowsPath(path).stem
        )
        if accepted and name.strip():
            self.paths[normalize_path(path)] = name.strip()
            self.refresh_custom()

    def remove_game(self) -> None:
        row = self.custom.currentRow()
        if row >= 0:
            del self.paths[list(self.paths)[row]]
            self.refresh_custom()

    def save(self) -> None:
        self.repository.set_custom_game_paths(self.paths)
        self.accept()

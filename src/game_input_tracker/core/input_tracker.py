from __future__ import annotations

from collections import Counter
from threading import Lock

from PySide6.QtCore import QObject, Signal


KEY_ALIASES = {
    "alt_l": "Alt",
    "alt_r": "Alt",
    "backspace": "Backspace",
    "caps_lock": "Caps Lock",
    "cmd": "Windows",
    "ctrl_l": "Ctrl",
    "ctrl_r": "Ctrl",
    "delete": "Delete",
    "down": "Down",
    "enter": "Enter",
    "esc": "Esc",
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
    "home": "Home",
    "insert": "Ins",
    "left": "Left",
    "page_down": "PgDn",
    "page_up": "PgUp",
    "right": "Right",
    "shift": "Shift",
    "shift_l": "Shift",
    "shift_r": "Shift",
    "space": "Space",
    "tab": "Tab",
    "up": "Up",
}


class InputTracker(QObject):
    counters_changed = Signal(int, int)
    active_inputs_changed = Signal(object)
    hook_error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._keyboard_listener = None
        self._mouse_listener = None
        self._active = False
        self._lock = Lock()
        self._key_counts: Counter[str] = Counter()
        self._mouse_counts: Counter[str] = Counter()
        self._session_key_total = 0
        self._session_mouse_total = 0
        self._active_inputs: set[str] = set()

    def start_hooks(self) -> None:
        try:
            from pynput import keyboard, mouse

            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
            )
            self._mouse_listener = mouse.Listener(on_click=self._on_click, on_scroll=self._on_scroll)
            self._keyboard_listener.start()
            self._mouse_listener.start()
        except Exception as exc:  # pragma: no cover - depends on OS hooks
            self.hook_error.emit(str(exc))

    def stop_hooks(self) -> None:
        for listener in (self._keyboard_listener, self._mouse_listener):
            if listener:
                listener.stop()
        self._keyboard_listener = None
        self._mouse_listener = None

    def begin_session(self) -> None:
        with self._lock:
            self._active = True
            self._key_counts.clear()
            self._mouse_counts.clear()
            self._session_key_total = 0
            self._session_mouse_total = 0
            self._active_inputs.clear()
        self.counters_changed.emit(0, 0)
        self.active_inputs_changed.emit(set())

    def end_session(self) -> tuple[Counter[str], Counter[str]]:
        with self._lock:
            self._active = False
            keys = self._key_counts.copy()
            mouse = self._mouse_counts.copy()
            self._key_counts.clear()
            self._mouse_counts.clear()
            self._session_key_total = 0
            self._session_mouse_total = 0
            self._active_inputs.clear()
        self.counters_changed.emit(0, 0)
        self.active_inputs_changed.emit(set())
        return keys, mouse

    def drain_counts(self) -> tuple[Counter[str], Counter[str]]:
        with self._lock:
            keys = self._key_counts.copy()
            mouse = self._mouse_counts.copy()
            self._key_counts.clear()
            self._mouse_counts.clear()
        return keys, mouse

    def _on_key_press(self, key) -> None:
        key_name = normalize_key(key)
        if not key_name:
            return
        with self._lock:
            if not self._active:
                return
            self._key_counts[key_name] += 1
            self._session_key_total += 1
            self._active_inputs.add(key_name)
            key_total = self._session_key_total
            mouse_total = self._session_mouse_total
            active_inputs = set(self._active_inputs)
        self.counters_changed.emit(key_total, mouse_total)
        self.active_inputs_changed.emit(active_inputs)

    def _on_key_release(self, key) -> None:
        key_name = normalize_key(key)
        if not key_name:
            return
        with self._lock:
            self._active_inputs.discard(key_name)
            active_inputs = set(self._active_inputs)
        self.active_inputs_changed.emit(active_inputs)

    def _on_click(self, _x, _y, button, pressed: bool) -> None:
        button_name = normalize_button(button)
        if not button_name:
            return
        with self._lock:
            if not self._active and pressed:
                return
            if not pressed:
                self._active_inputs.discard(button_name)
                active_inputs = set(self._active_inputs)
            else:
                self._mouse_counts[button_name] += 1
                self._session_mouse_total += 1
                self._active_inputs.add(button_name)
                key_total = self._session_key_total
                mouse_total = self._session_mouse_total
                active_inputs = set(self._active_inputs)
        if pressed:
            self.counters_changed.emit(key_total, mouse_total)
        self.active_inputs_changed.emit(active_inputs)

    def _on_scroll(self, _x, _y, _dx, dy) -> None:
        button_name = "Scroll Up" if dy > 0 else "Scroll Down"
        with self._lock:
            if not self._active:
                return
            self._mouse_counts[button_name] += 1
            self._session_mouse_total += 1
            key_total = self._session_key_total
            mouse_total = self._session_mouse_total
            active_inputs = set(self._active_inputs)
        self.counters_changed.emit(key_total, mouse_total)
        self.active_inputs_changed.emit(active_inputs)


def normalize_key(key) -> str | None:
    char = getattr(key, "char", None)
    if char:
        if char.isprintable() and len(char) == 1:
            return char.upper()
        return None
    raw = str(key).replace("Key.", "").replace("'", "")
    return KEY_ALIASES.get(raw, raw.replace("_", " ").title())


def normalize_button(button) -> str | None:
    raw = str(button).replace("Button.", "").lower()
    if raw == "left":
        return "Left Click"
    if raw == "right":
        return "Right Click"
    if raw == "middle":
        return "Middle Click"
    return raw.title()

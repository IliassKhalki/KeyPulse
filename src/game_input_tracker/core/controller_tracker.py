from __future__ import annotations

import ctypes
from ctypes import wintypes

from PySide6.QtCore import QObject, QTimer, Signal


XINPUT_GAMEPAD_DPAD_UP = 0x0001
XINPUT_GAMEPAD_DPAD_DOWN = 0x0002
XINPUT_GAMEPAD_DPAD_LEFT = 0x0004
XINPUT_GAMEPAD_DPAD_RIGHT = 0x0008
XINPUT_GAMEPAD_START = 0x0010
XINPUT_GAMEPAD_BACK = 0x0020
XINPUT_GAMEPAD_LEFT_THUMB = 0x0040
XINPUT_GAMEPAD_RIGHT_THUMB = 0x0080
XINPUT_GAMEPAD_LEFT_SHOULDER = 0x0100
XINPUT_GAMEPAD_RIGHT_SHOULDER = 0x0200
XINPUT_GAMEPAD_A = 0x1000
XINPUT_GAMEPAD_B = 0x2000
XINPUT_GAMEPAD_X = 0x4000
XINPUT_GAMEPAD_Y = 0x8000

THUMB_DEADZONE = 9000
TRIGGER_THRESHOLD = 30


class XInputGamepad(ctypes.Structure):
    _fields_ = [
        ("wButtons", wintypes.WORD),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]


class XInputState(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", wintypes.DWORD),
        ("Gamepad", XInputGamepad),
    ]


class ControllerTracker(QObject):
    active_controller_inputs_changed = Signal(object)

    def __init__(self, poll_interval_ms: int = 33) -> None:
        super().__init__()
        self._xinput = load_xinput()
        self._timer = QTimer(self)
        self._timer.setInterval(poll_interval_ms)
        self._timer.timeout.connect(self.poll)
        self._last_active: set[str] = set()

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def poll(self) -> None:
        active: set[str] = set()
        if self._xinput is not None:
            for index in range(4):
                state = XInputState()
                result = self._xinput.XInputGetState(index, ctypes.byref(state))
                if result == 0:
                    active.update(active_inputs_from_gamepad(state.Gamepad))
                    active.add("Controller Connected")
                    break
        if active != self._last_active:
            self._last_active = active
            self.active_controller_inputs_changed.emit(active)


def load_xinput():
    for library in ("xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"):
        try:
            dll = ctypes.WinDLL(library)
            dll.XInputGetState.argtypes = [wintypes.DWORD, ctypes.POINTER(XInputState)]
            dll.XInputGetState.restype = wintypes.DWORD
            return dll
        except OSError:
            continue
    return None


def active_inputs_from_gamepad(gamepad: XInputGamepad) -> set[str]:
    buttons = gamepad.wButtons
    active: set[str] = set()
    mapping = {
        XINPUT_GAMEPAD_DPAD_UP: "D-Up",
        XINPUT_GAMEPAD_DPAD_DOWN: "D-Down",
        XINPUT_GAMEPAD_DPAD_LEFT: "D-Left",
        XINPUT_GAMEPAD_DPAD_RIGHT: "D-Right",
        XINPUT_GAMEPAD_START: "Start",
        XINPUT_GAMEPAD_BACK: "Back",
        XINPUT_GAMEPAD_LEFT_THUMB: "L3",
        XINPUT_GAMEPAD_RIGHT_THUMB: "R3",
        XINPUT_GAMEPAD_LEFT_SHOULDER: "LB/L1",
        XINPUT_GAMEPAD_RIGHT_SHOULDER: "RB/R1",
        XINPUT_GAMEPAD_A: "A/Cross",
        XINPUT_GAMEPAD_B: "B/Circle",
        XINPUT_GAMEPAD_X: "X/Square",
        XINPUT_GAMEPAD_Y: "Y/Triangle",
    }
    for mask, label in mapping.items():
        if buttons & mask:
            active.add(label)
    if gamepad.bLeftTrigger > TRIGGER_THRESHOLD:
        active.add("LT/L2")
    if gamepad.bRightTrigger > TRIGGER_THRESHOLD:
        active.add("RT/R2")
    add_axis_inputs(active, "LS", gamepad.sThumbLX, gamepad.sThumbLY)
    add_axis_inputs(active, "RS", gamepad.sThumbRX, gamepad.sThumbRY)
    return active


def add_axis_inputs(active: set[str], prefix: str, x_value: int, y_value: int) -> None:
    if x_value <= -THUMB_DEADZONE:
        active.add(f"{prefix} Left")
    elif x_value >= THUMB_DEADZONE:
        active.add(f"{prefix} Right")
    if y_value <= -THUMB_DEADZONE:
        active.add(f"{prefix} Down")
    elif y_value >= THUMB_DEADZONE:
        active.add(f"{prefix} Up")

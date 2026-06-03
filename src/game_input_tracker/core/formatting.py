from __future__ import annotations


def compact_number(value: int | float) -> str:
    number = float(value or 0)
    for suffix in ("", "K", "M", "B"):
        if abs(number) < 1000 or suffix == "B":
            if suffix:
                return f"{number:.1f}{suffix}".replace(".0", "")
            return f"{int(number):,}"
        number /= 1000
    return str(value)


def format_duration(seconds: int | float) -> str:
    seconds = int(seconds or 0)
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if hours >= 1000:
        return f"{hours:,}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


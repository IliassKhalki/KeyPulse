from __future__ import annotations


def compact_number(value: int | float) -> str:
    number = float(value or 0)
    suffixes = ("", "K", "M", "B")
    for index, suffix in enumerate(suffixes):
        if abs(number) < 1000 or suffix == suffixes[-1]:
            if suffix:
                rounded = round(number, 1)
                if abs(rounded) >= 1000 and index < len(suffixes) - 1:
                    number = rounded / 1000
                    next_suffix = suffixes[index + 1]
                    return f"{number:.1f}{next_suffix}".replace(".0", "")
                return f"{rounded:.1f}{suffix}".replace(".0", "")
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

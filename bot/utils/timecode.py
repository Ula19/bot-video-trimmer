"""Утилиты для работы с тайм-кодами

Поддерживаем форматы:
  - SS / SSs           (например "90" или "90s" → 90)
  - MM:SS              (например "5:30" → 330)
  - HH:MM:SS           (например "1:23:45" → 5025)

Для validate_trim_range — кидаем ValueError с i18n-ключами:
  - "error_timecode"
  - "error_end_before_start"
  - "error_out_of_bounds"
"""
from __future__ import annotations

import re


# допустимый формат: цифры + опциональные ":XX" группы + опциональный "s"
# Первое число — без ограничения длины (для формата "только секунды": 1500 → 25:00),
# последующие группы минут/секунд — по 2 цифры. Итоговая верхняя граница
# проверяется явно после парсинга (_MAX_TIMECODE_SECONDS).
_TIMECODE_RE = re.compile(
    r"^\s*(\d+)(?::(\d{1,2}))?(?::(\d{1,2}))?\s*s?\s*$"
)

# верхняя граница тайм-кода — 24 часа. Больше — ошибка.
_MAX_TIMECODE_SECONDS = 24 * 60 * 60  # 86400


def parse_timecode(value: str) -> int:
    """Парсит строку тайм-кода в секунды (int).

    Принимает форматы:
      - "90"       → 90
      - "90s"      → 90
      - "5:30"     → 330   (MM:SS)
      - "1:23:45"  → 5025  (HH:MM:SS)

    При невалидном вводе — бросает ValueError("error_timecode")
    (ключ i18n, примеры форматов подставляет хендлер).
    """
    if value is None:
        raise ValueError("error_timecode")

    s = str(value).strip()
    if not s:
        raise ValueError("error_timecode")

    # поддерживаем "1h2m3s" → пока НЕ поддерживаем, только цифровой формат
    m = _TIMECODE_RE.match(s)
    if not m:
        raise ValueError("error_timecode")

    groups = [g for g in m.groups() if g is not None]
    # groups — это от 1 до 3 чисел, последовательно
    try:
        parts = [int(g) for g in groups]
    except ValueError:
        raise ValueError("error_timecode")

    # 1 число — секунды
    # 2 числа — минуты:секунды
    # 3 числа — часы:минуты:секунды
    if len(parts) == 1:
        hours, minutes, seconds = 0, 0, parts[0]
    elif len(parts) == 2:
        hours, minutes, seconds = 0, parts[0], parts[1]
    elif len(parts) == 3:
        hours, minutes, seconds = parts[0], parts[1], parts[2]
    else:
        raise ValueError("error_timecode")

    # минуты и секунды должны быть в пределах 0..59 (если в старших группах есть значения)
    if len(parts) >= 2 and (minutes >= 60 or minutes < 0):
        raise ValueError("error_timecode")
    if len(parts) >= 2 and (seconds >= 60 or seconds < 0):
        raise ValueError("error_timecode")
    if hours < 0 or minutes < 0 or seconds < 0:
        raise ValueError("error_timecode")

    total = hours * 3600 + minutes * 60 + seconds
    # верхняя граница — 24 часа (защита от мусорных значений вроде "999999999")
    if total > _MAX_TIMECODE_SECONDS:
        raise ValueError("error_timecode")
    return int(total)


def format_timecode(seconds: int | float) -> str:
    """Форматирует секунды в строку HH:MM:SS."""
    if seconds is None:
        return "00:00:00"
    try:
        total = int(round(float(seconds)))
    except (TypeError, ValueError):
        return "00:00:00"
    if total < 0:
        total = 0
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def validate_trim_range(start: int, end: int, duration: int) -> int:
    """Проверяет корректность диапазона обрезки. Клампит end до duration.

    Бросает ValueError с i18n-ключом:
      - "error_timecode"          — невалидные значения
      - "error_end_before_start"  — конец не позже начала
      - "error_out_of_bounds"     — start за пределами видео

    Возвращает скорректированный end (если был больше duration — обрезается до конца).
    """
    if start is None or end is None:
        raise ValueError("error_timecode")
    if start < 0 or end < 0:
        raise ValueError("error_timecode")
    if end <= start:
        raise ValueError("error_end_before_start")
    if duration and start >= int(duration):
        raise ValueError("error_out_of_bounds")
    # если end за пределами — клампим до конца видео
    if duration and end > int(duration):
        end = int(duration)
    return end

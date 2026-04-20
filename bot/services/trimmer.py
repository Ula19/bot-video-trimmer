"""Сервис обрезки видео через ffmpeg / ffprobe.

Ответственность:
  - получить длительность видео (ffprobe)
  - обрезать видео (ffmpeg) в режиме fast (stream copy) или precise (re-encode)

ВСЁ выполняется через asyncio.create_subprocess_exec — без shell=True,
без subprocess.run (не блокируем event loop).

Доменные ошибки — TrimmerError.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


class TrimmerError(Exception):
    """Доменная ошибка сервиса обрезки."""


# лимит параллельных ffmpeg-обработок (CPU-тяжёлые, не стоит ставить много)
_trim_semaphore = asyncio.Semaphore(5)

# таймауты на внешние процессы ffmpeg/ffprobe (секунды)
# 10 минут — достаточно даже для точной перекодировки больших видео,
# но гарантированно освобождает слот семафора при зависании
_FFMPEG_TIMEOUT = 600
_FFPROBE_TIMEOUT = 60


async def get_video_info(path: Path) -> dict:
    """Возвращает duration, width, height видео через ffprobe (один вызов)."""
    p = Path(path)
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "default=nw=1",
        str(p),
    ]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise TrimmerError(f"ffprobe не найден: {exc}") from exc

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=_FFPROBE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        try:
            process.kill()
            await process.wait()
        except Exception:
            pass
        raise TrimmerError("ffprobe timeout")

    if process.returncode != 0:
        err = stderr.decode(errors="replace").strip()
        raise TrimmerError(f"ffprobe returncode={process.returncode}: {err}")

    # парсим вывод вида "width=1920\nheight=1080\nduration=123.456"
    info: dict = {}
    for line in stdout.decode(errors="replace").splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            info[k.strip()] = v.strip()

    try:
        duration = float(info.get("duration", 0))
    except ValueError:
        duration = 0.0
    try:
        width = int(info.get("width", 0))
    except ValueError:
        width = 0
    try:
        height = int(info.get("height", 0))
    except ValueError:
        height = 0

    return {"duration": duration, "width": width, "height": height}


async def get_video_duration(path: Path) -> float:
    """Возвращает длительность видео в секундах через ffprobe.

    Бросает TrimmerError если ffprobe вернул ошибку или невалидное значение.
    """
    p = Path(path)
    if not p.exists():
        raise TrimmerError(f"файл не найден: {p}")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1",
        str(p),
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise TrimmerError(f"ffprobe не найден: {exc}") from exc
    except Exception as exc:
        raise TrimmerError(f"ffprobe: ошибка запуска: {exc}") from exc

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=_FFPROBE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        # процесс завис — убиваем и отдаём ошибку
        try:
            process.kill()
        except ProcessLookupError:
            pass
        try:
            await process.wait()
        except Exception:
            pass
        logger.error("ffprobe: таймаут %s сек на файле %s", _FFPROBE_TIMEOUT, p)
        raise TrimmerError("ffprobe timeout")

    if process.returncode != 0:
        err = stderr.decode(errors="replace").strip()
        logger.error("ffprobe не смог прочитать %s: %s", p, err)
        raise TrimmerError(f"ffprobe returncode={process.returncode}: {err}")

    raw = stdout.decode(errors="replace").strip()
    if not raw:
        raise TrimmerError("ffprobe вернул пустой ответ")
    try:
        duration = float(raw)
    except ValueError as exc:
        raise TrimmerError(f"ffprobe вернул невалидное значение: {raw!r}") from exc

    if duration <= 0:
        raise TrimmerError(f"некорректная длительность: {duration}")

    return duration


async def trim_video(
    input_path: Path,
    output_path: Path,
    start: int,
    end: int,
    mode: Literal["fast", "precise"] = "fast",
) -> None:
    """Обрезает видео от start до end (секунды).

    Режимы:
      - "fast"    — -c copy (stream copy, быстро, по keyframe)
      - "precise" — re-encode (libx264 + aac, медленно, но точно)

    ВАЖНО: синтаксис `-ss <start> -to <end>` перед `-i` (input seeking)
    работает быстрее; для precise-режима re-encode всё равно идёт по всему куску.

    Бросает TrimmerError при ошибке ffmpeg или некорректных аргументах.
    """
    inp = Path(input_path)
    out = Path(output_path)

    if not inp.exists():
        raise TrimmerError(f"входной файл не найден: {inp}")

    if start < 0 or end <= start:
        raise TrimmerError(f"некорректный диапазон: {start}..{end}")

    if mode not in ("fast", "precise"):
        raise TrimmerError(f"неизвестный режим: {mode!r}")

    # гарантируем что родительская директория для output существует
    out.parent.mkdir(parents=True, exist_ok=True)

    if mode == "fast":
        # -ss перед -i: быстрый seek до ближайшего keyframe ДО start
        # -t вместо -to: длительность от точки seek, а не абсолютное время
        # итог: длительность точная, но начало может сдвинуться на ±1-2 сек к keyframe
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-ss", str(start),
            "-i", str(inp),
            "-t", str(end - start),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            str(out),
        ]
    else:
        # precise — re-encode; ставим -ss перед -i для быстрого seek,
        # -to должен считаться от того же нуля (т.к. -ss до -i сдвигает тайм)
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-ss", str(start),
            "-to", str(end),
            "-i", str(inp),
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(out),
        ]

    async with _trim_semaphore:
        logger.info(
            "ffmpeg: обрезка %s → %s (start=%s, end=%s, mode=%s)",
            inp.name, out.name, start, end, mode,
        )
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise TrimmerError(f"ffmpeg не найден: {exc}") from exc
        except Exception as exc:
            raise TrimmerError(f"ffmpeg: ошибка запуска: {exc}") from exc

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=_FFMPEG_TIMEOUT,
            )
        except asyncio.TimeoutError:
            # процесс завис — убиваем и чистим частичный output
            try:
                process.kill()
            except ProcessLookupError:
                pass
            try:
                await process.wait()
            except Exception:
                pass
            try:
                if out.exists():
                    out.unlink()
            except OSError:
                pass
            logger.error(
                "ffmpeg: таймаут %s сек на файле %s", _FFMPEG_TIMEOUT, inp,
            )
            raise TrimmerError("ffmpeg timeout")

        if process.returncode != 0:
            err = stderr.decode(errors="replace").strip()
            logger.error(
                "ffmpeg returncode=%s, stderr=%s", process.returncode, err,
            )
            # не оставляем битый output
            try:
                if out.exists():
                    out.unlink()
            except OSError:
                pass
            raise TrimmerError(
                f"ffmpeg returncode={process.returncode}: {err[:500]}"
            )

    if not out.exists() or out.stat().st_size == 0:
        raise TrimmerError("ffmpeg отработал, но выходной файл пуст")


def classify_error(exc: BaseException) -> str:
    """Классифицирует исключение для выбора i18n-сообщения.

    Категории:
      - file_too_large
      - unsupported_format
      - ffmpeg_error
      - network
      - unknown
    """
    if isinstance(exc, TrimmerError):
        msg = str(exc).lower()
        if "timeout" in msg:
            # ffmpeg/ffprobe подвис — это по сути ошибка обработки
            return "ffmpeg_error"
        if "too large" in msg or "file too large" in msg:
            return "file_too_large"
        if "invalid data" in msg or "no such" in msg or "not found" in msg:
            return "unsupported_format"
        return "ffmpeg_error"
    if isinstance(exc, asyncio.TimeoutError):
        return "network"
    name = type(exc).__name__.lower()
    if "timeout" in name or "network" in name or "connection" in name:
        return "network"
    return "unknown"

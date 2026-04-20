"""Хэндлер обрезки видео — FSM-флоу.

Состояния:
  1. waiting_video  — ждём видеофайл (default; старт через callback trim_video или /start)
  2. waiting_start  — ждём тайм-код начала
  3. waiting_end    — ждём тайм-код конца
  4. waiting_mode   — ждём выбор режима (fast/precise)
  5. processing     — обрабатываем файл (новые сообщения блокируем сообщением "busy")

Cleanup — явный, синхронно по завершении хендлера и в /cancel.
Local Bot API сам файлы не чистит — мы обязаны удалять tmp_dir целиком.
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.database import async_session
from bot.database.crud import (
    get_user_language,
    increment_user_trim_count,
)
from bot.emojis import E
from bot.i18n import t
from bot.keyboards.inline import (
    get_back_keyboard,
    get_start_keyboard,
    get_trim_cancel_keyboard,
    get_trim_mode_keyboard,
)
from bot.services.trimmer import (
    get_video_info,
    TrimmerError,
    classify_error,
    get_video_duration,
    trim_video,
)
from bot.utils.fsm_cleanup import cleanup_state
from bot.utils.timecode import (
    format_timecode,
    parse_timecode,
    validate_trim_range,
)

logger = logging.getLogger(__name__)
router = Router()

# рабочая директория для временных файлов
TMP_ROOT = "/tmp/trimmer_bot"

# максимальный размер результата (Telegram-лимит с Local Bot API)
MAX_OUTPUT_SIZE = int(1.9 * 1024 * 1024 * 1024)  # 1.9 ГБ

# максимальный размер входа (на всякий случай — Local Bot API принимает до 2 ГБ)
MAX_INPUT_SIZE = 2 * 1024 * 1024 * 1024  # 2 ГБ


class TrimStates(StatesGroup):
    waiting_video = State()
    waiting_start = State()
    waiting_end = State()
    waiting_mode = State()
    processing = State()


# пер-юзер локи для защиты от двойного клика (race на смену state).
# Берём лок в начале handle_trim_mode, на занятом — отвечаем busy.
_user_locks: dict[int, asyncio.Lock] = {}


def _get_user_lock(user_id: int) -> asyncio.Lock:
    """Возвращает (создаёт при необходимости) лок для юзера."""
    lock = _user_locks.get(user_id)
    if lock is None:
        lock = asyncio.Lock()
        _user_locks[user_id] = lock
    return lock


# ---------- утилиты ----------

def _fmt_size(num_bytes: int | float | None) -> str:
    """Человеко-понятный размер файла."""
    if not num_bytes:
        return "?"
    n = float(num_bytes)
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024 or unit == "ГБ":
            return f"{n:.1f} {unit}" if unit != "Б" else f"{int(n)} {unit}"
        n /= 1024
    return f"{n:.1f} ГБ"


async def _get_lang(user_id: int) -> str:
    async with async_session() as session:
        return await get_user_language(session, user_id)


# ---------- приём видео ----------

@router.message(F.video | F.document | F.animation)
async def handle_video(message: Message, state: FSMContext) -> None:
    """Принимает видео/документ-видео.

    Срабатывает из любого state (кроме processing и waiting_start/end/mode —
    в них вход трактуется иначе). Если юзер прислал новое видео посреди
    процесса — сбрасываем старое и начинаем заново.
    """
    current = await state.get_state()
    lang = await _get_lang(message.from_user.id)

    # если идёт обработка — просим дождаться
    if current == TrimStates.processing.state:
        await message.answer(t("trim.busy", lang), parse_mode="HTML")
        return

    # сначала определяем источник файла и валидируем ДО cleanup —
    # чтобы pdf или невалидный документ не сбросил активный FSM
    video = message.video
    document = message.document
    animation = message.animation

    if video is not None:
        file_id = video.file_id
        file_size = video.file_size or 0
        file_name_hint = video.file_name or f"video_{video.file_unique_id}.mp4"
    elif animation is not None:
        file_id = animation.file_id
        file_size = animation.file_size or 0
        file_name_hint = animation.file_name or f"animation_{animation.file_unique_id}.mp4"
    elif document is not None:
        mime = (document.mime_type or "").lower()
        if not mime.startswith("video/"):
            await message.answer(t("trim.error_not_video", lang), parse_mode="HTML")
            return
        file_id = document.file_id
        file_size = document.file_size or 0
        file_name_hint = document.file_name or f"video_{document.file_unique_id}.mp4"
    else:
        await message.answer(t("trim.error_not_video", lang), parse_mode="HTML")
        return

    # CRITICAL: проверку размера ДО cleanup — чтобы большое видео не сбросило
    # активную сессию обрезки юзера (иначе прогресс потерян зря)
    if file_size and file_size > MAX_INPUT_SIZE:
        await message.answer(t("error.too_large", lang), parse_mode="HTML")
        return

    # если уже ждём тайм-код или режим — предыдущее видео лежит в FSM,
    # сбрасываем и принимаем новое (tmp_dir старого видео удалится)
    if current in (
        TrimStates.waiting_start.state,
        TrimStates.waiting_end.state,
        TrimStates.waiting_mode.state,
    ):
        await cleanup_state(state)

    # подготавливаем tmp-директорию — НЕ используем контекстный менеджер,
    # так как директория должна жить между FSM-хендлерами
    os.makedirs(TMP_ROOT, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="trim_", dir=TMP_ROOT)

    # имя файла — безопасное, в пределах tmp_dir
    safe_name = Path(file_name_hint).name or "input.mp4"
    input_path = str(Path(tmp_dir) / safe_name)

    status_msg = await message.answer(
        f"{E['clock']} Скачиваю видео...", parse_mode="HTML",
    )

    try:
        file_obj = await message.bot.get_file(file_id)
        api_file_path: str = file_obj.file_path  # type: ignore[assignment]

        # Local Bot API возвращает абсолютный путь вида /var/lib/telegram-bot-api/...
        # Перемещаем файл в нашу tmp_dir — он автоматически пропадает из bot-api-data
        if api_file_path and api_file_path.startswith("/"):
            shutil.move(api_file_path, input_path)
        else:
            # fallback: стандартный API — качаем через download_file
            await message.bot.download_file(api_file_path, destination=input_path)
    except Exception as exc:
        logger.exception("download: не удалось получить file_id=%s: %s", file_id, exc)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        try:
            await status_msg.edit_text(
                t("trim.error_download", lang), parse_mode="HTML",
            )
        except Exception:
            await message.answer(t("trim.error_download", lang), parse_mode="HTML")
        return

    # читаем длительность
    try:
        duration_f = await get_video_duration(Path(input_path))
    except TrimmerError as exc:
        logger.warning("ffprobe: %s", exc)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        try:
            await status_msg.edit_text(
                t("trim.error_ffmpeg", lang), parse_mode="HTML",
            )
        except Exception:
            await message.answer(t("trim.error_ffmpeg", lang), parse_mode="HTML")
        return

    duration = int(round(duration_f))

    # сохраняем в FSM и переходим к waiting_start
    await state.set_state(TrimStates.waiting_start)
    await state.update_data(
        tmp_dir=tmp_dir,
        input_path=input_path,
        duration=duration,
        file_size=file_size,
    )

    try:
        await status_msg.edit_text(
            t(
                "trim.video_received", lang,
                duration=format_timecode(duration),
                size=_fmt_size(file_size or os.path.getsize(input_path)),
            ),
            reply_markup=get_trim_cancel_keyboard(lang),
            parse_mode="HTML",
        )
    except Exception:
        await message.answer(
            t(
                "trim.video_received", lang,
                duration=format_timecode(duration),
                size=_fmt_size(file_size or os.path.getsize(input_path)),
            ),
            reply_markup=get_trim_cancel_keyboard(lang),
            parse_mode="HTML",
        )


# ---------- приём тайм-кода начала ----------

@router.message(TrimStates.waiting_start, F.text)
async def handle_start_time(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(message.from_user.id)
    text = (message.text or "").strip()

    # /cancel и прочие команды обрабатываются отдельными хендлерами
    if text.startswith("/"):
        return

    try:
        start = parse_timecode(text)
    except ValueError:
        await message.answer(
            t("trim.error_timecode", lang),
            reply_markup=get_trim_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    duration = int(data.get("duration") or 0)

    # сразу валидируем что старт в пределах видео
    if duration and start >= duration:
        await message.answer(
            t(
                "trim.error_out_of_bounds", lang,
                duration=format_timecode(duration),
            ),
            reply_markup=get_trim_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    await state.update_data(start=start)
    await state.set_state(TrimStates.waiting_end)

    await message.answer(
        t("trim.send_end", lang, start=format_timecode(start)),
        reply_markup=get_trim_cancel_keyboard(lang),
        parse_mode="HTML",
    )


# ---------- приём тайм-кода конца ----------

@router.message(TrimStates.waiting_end, F.text)
async def handle_end_time(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(message.from_user.id)
    text = (message.text or "").strip()

    if text.startswith("/"):
        return

    try:
        end = parse_timecode(text)
    except ValueError:
        await message.answer(
            t("trim.error_timecode", lang),
            reply_markup=get_trim_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    start = int(data.get("start") or 0)
    duration = int(data.get("duration") or 0)

    try:
        end = validate_trim_range(start, end, duration)
    except ValueError as exc:
        key = str(exc)
        if key == "error_end_before_start":
            msg = t("trim.error_end_before_start", lang)
        elif key == "error_out_of_bounds":
            msg = t(
                "trim.error_out_of_bounds", lang,
                duration=format_timecode(duration),
            )
        else:
            msg = t("trim.error_timecode", lang)
        await message.answer(
            msg,
            reply_markup=get_trim_cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    await state.update_data(end=end)
    await state.set_state(TrimStates.waiting_mode)

    await message.answer(
        t(
            "trim.choose_mode", lang,
            start=format_timecode(start),
            end=format_timecode(end),
        ),
        reply_markup=get_trim_mode_keyboard(lang),
        parse_mode="HTML",
    )


# ---------- выбор режима и обработка ----------

@router.callback_query(TrimStates.waiting_mode, F.data.startswith("trim_mode:"))
async def handle_trim_mode(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(callback.from_user.id)
    mode = callback.data.split(":", 1)[1]
    if mode not in ("fast", "precise"):
        await callback.answer()
        return

    # CRITICAL: защита от двойного клика.
    # Проверка lock.locked() безопасна — между ней и `async with lock:`
    # нет await'ов, значит event loop не переключит задачу (корутины
    # кооперативны). Первый клик возьмёт лок, второй увидит locked=True.
    lock = _get_user_lock(callback.from_user.id)
    if lock.locked():
        # предыдущий клик ещё обрабатывается — показываем busy через alert
        try:
            await callback.answer(t("trim.busy", lang), show_alert=True)
        except Exception:
            pass
        return

    async with lock:
        # повторно проверяем текущий state — второй callback мог
        # проскочить фильтр, если оба пришли до set_state
        current = await state.get_state()
        if current != TrimStates.waiting_mode.state:
            # кто-то уже обрабатывает (processing) либо state уже сброшен
            await callback.answer()
            return

        data = await state.get_data()
        tmp_dir = data.get("tmp_dir")
        input_path = data.get("input_path")
        start = int(data.get("start") or 0)
        end = int(data.get("end") or 0)

        if not tmp_dir or not input_path or not os.path.exists(input_path):
            await cleanup_state(state)
            try:
                await callback.message.edit_text(
                    t("trim.error_download", lang),
                    reply_markup=get_back_keyboard(lang),
                    parse_mode="HTML",
                )
            except Exception:
                pass
            await callback.answer()
            return

        # атомарно переводим state в processing ДО любых await edit_text —
        # второй клик в фильтре waiting_mode не пройдёт
        await state.set_state(TrimStates.processing)

        # гасим "часики" на кнопке и меняем сообщение на "обрабатываю"
        await callback.answer()
        try:
            await callback.message.edit_text(
                t("trim.processing", lang), parse_mode="HTML",
            )
        except Exception:
            pass

        output_path = str(
            Path(tmp_dir) / f"trim_{start}_{end}_{mode}.mp4"
        )

        success = False
        try:
            await trim_video(
                input_path=Path(input_path),
                output_path=Path(output_path),
                start=start,
                end=end,
                mode=mode,  # type: ignore[arg-type]
            )

            size = os.path.getsize(output_path)
            if size > MAX_OUTPUT_SIZE:
                try:
                    await callback.message.answer(
                        t("trim.error_too_big", lang),
                        reply_markup=get_back_keyboard(lang),
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
                return

            # получаем размеры выходного файла для передачи Telegram
            try:
                out_info = await get_video_info(Path(output_path))
            except Exception:
                out_info = {"duration": end - start, "width": 0, "height": 0}

            # отправляем видео с точными метаданными
            try:
                await callback.message.answer_video(
                    video=FSInputFile(output_path),
                    caption=t("trim.done", lang),
                    parse_mode="HTML",
                    duration=int(out_info["duration"]) or (end - start),
                    width=out_info["width"] or None,
                    height=out_info["height"] or None,
                    supports_streaming=True,
                )
                success = True
            except Exception as exc:
                logger.exception("send_video: %s", exc)
                try:
                    await callback.message.answer_document(
                        document=FSInputFile(output_path),
                        caption=t("trim.done", lang),
                        parse_mode="HTML",
                    )
                    success = True
                except Exception as exc2:
                    logger.exception("send_document fallback: %s", exc2)
                    await callback.message.answer(
                        t("error.generic", lang), parse_mode="HTML",
                    )

            if success:
                async with async_session() as session:
                    await increment_user_trim_count(session, callback.from_user.id)

                pass

        except TrimmerError as exc:
            category = classify_error(exc)
            logger.warning("trim_video: %s (%s)", exc, category)
            msg_key = {
                "file_too_large": "trim.error_too_big",
                "unsupported_format": "trim.error_not_video",
                "ffmpeg_error": "trim.error_ffmpeg",
                "network": "error.timeout",
            }.get(category, "trim.error_ffmpeg")
            try:
                await callback.message.answer(
                    t(msg_key, lang),
                    reply_markup=get_back_keyboard(lang),
                    parse_mode="HTML",
                )
            except Exception:
                pass
        except Exception as exc:
            logger.exception("trim: неизвестная ошибка: %s", exc)
            try:
                await callback.message.answer(
                    t("error.generic", lang),
                    reply_markup=get_back_keyboard(lang),
                    parse_mode="HTML",
                )
            except Exception:
                pass
        finally:
            # CRITICAL: всегда чистим tmp_dir и сбрасываем state
            await cleanup_state(state)


# ---------- отмена ----------

@router.callback_query(F.data == "trim_cancel")
async def trim_cancel_callback(
    callback: CallbackQuery, state: FSMContext,
) -> None:
    lang = await _get_lang(callback.from_user.id)
    current = await state.get_state()

    # посреди обработки отменять нельзя
    if current == TrimStates.processing.state:
        await callback.answer(t("trim.busy", lang), show_alert=True)
        return

    await cleanup_state(state)
    try:
        await callback.message.edit_text(
            t("trim.cancelled", lang),
            reply_markup=get_start_keyboard(
                user_id=callback.from_user.id, lang=lang,
            ),
            parse_mode="HTML",
        )
    except Exception:
        await callback.message.answer(
            t("trim.cancelled", lang),
            reply_markup=get_start_keyboard(
                user_id=callback.from_user.id, lang=lang,
            ),
            parse_mode="HTML",
        )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(message.from_user.id)
    current = await state.get_state()

    if current == TrimStates.processing.state:
        await message.answer(t("trim.busy", lang), parse_mode="HTML")
        return

    await cleanup_state(state)
    await message.answer(
        t("trim.cancelled", lang),
        reply_markup=get_start_keyboard(
            user_id=message.from_user.id, lang=lang,
        ),
        parse_mode="HTML",
    )


# ---------- подсказка на любое другое сообщение, пока ждём видео ----------

@router.message(F.text, TrimStates.waiting_video)
async def _prompt_video(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(message.from_user.id)
    # пропускаем команды (их обработают другие роутеры / /cancel)
    if message.text and message.text.startswith("/"):
        return
    await message.answer(
        t("trim.send_video", lang),
        reply_markup=get_trim_cancel_keyboard(lang),
        parse_mode="HTML",
    )

"""Shared helpers."""
import os

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, Message


async def safe_edit(message: Message, text: str, reply_markup=None, **kwargs) -> None:
    """Edit a message's text (or caption if it is a media message). If the
    message can't be edited (old media message, not modified, deleted),
    sends the content as a new message instead of crashing."""
    try:
        await message.edit_text(text, reply_markup=reply_markup, **kwargs)
        return
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return
    except Exception:
        pass
    try:
        await message.edit_caption(caption=text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            await message.answer(text, reply_markup=reply_markup)
    except Exception:
        await message.answer(text, reply_markup=reply_markup)


async def send_page(message: Message, text: str, reply_markup=None,
                    photo: str | None = None) -> None:
    """Open a page: if an image file exists for it, re-send the message as a
    photo with the text in the caption (edits can't attach a photo to an
    existing message); otherwise fall back to a plain text edit."""
    if photo and os.path.exists(photo):
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await message.answer_photo(
                FSInputFile(photo), caption=text, reply_markup=reply_markup)
            return
        except Exception:
            pass
    await safe_edit(message, text, reply_markup=reply_markup)

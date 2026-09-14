"""Holds the running Bot instance so any module can reach it without
circular imports (handlers are imported by bot.py, so they must not import
bot.py back)."""
from aiogram import Bot

_bot: Bot | None = None


def set_bot(bot: Bot) -> None:
    global _bot
    _bot = bot


def get_bot() -> Bot:
    if _bot is None:
        raise RuntimeError("Bot is not initialized yet")
    return _bot

"""Middlewares: inject DB session and current user into every update."""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession

from database import queries
from database.database import session_factory
from database.models import User


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with session_factory() as session:
            data["session"] = session
            return await handler(event, data)


class UserMiddleware(BaseMiddleware):
    """Create/refresh the user row and put the model into data['user']."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TelegramUser | None = data.get("event_from_user")
        session: AsyncSession | None = data.get("session")
        if tg_user is None or session is None or tg_user.is_bot:
            return await handler(event, data)
        user: User = await queries.get_or_create_user(session, tg_user)
        data["user"] = user
        return await handler(event, data)

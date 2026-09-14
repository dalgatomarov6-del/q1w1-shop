"""Metro Royale Shop — Telegram bot entrypoint."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import queries
from database.database import init_db, session_factory
from middlewares import DbSessionMiddleware, UserMiddleware
from services import payments as payment_service

import runtime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("bot")


async def on_startup() -> None:
    async with session_factory() as session:
        settings = await queries.get_all_settings(session)
    # Wire payment confirmation to admin/user notifications + referral rewards
    async def on_payment(order_id: int) -> None:
        bot = runtime.get_bot()
        from services.orders import notify_admin_payment, notify_user_paid
        await notify_admin_payment(bot, order_id)
        await notify_user_paid(bot, order_id)
        async with session_factory() as s:
            s_settings = await queries.get_all_settings(s)
            order = await queries.get_order(s, order_id)
            if order is not None:
                await queries.reward_referrals_for_order(
                    s, order,
                    percent=float(s_settings["referral_reward_percent"]),
                    fixed=float(s_settings["referral_reward_fixed"]),
                )

    payment_service.register_on_payment(on_payment)


async def main() -> None:
    if not config.bot_token:
        logger.critical("BOT_TOKEN is not configured in .env")
        sys.exit(1)

    await init_db()

    _bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    runtime.set_bot(_bot)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(UserMiddleware())

    from handlers import (admin, orders, payments, profile, promo, referrals,
                          shop, start, support)
    dp.include_router(start.router)
    dp.include_router(shop.router)
    dp.include_router(payments.router)
    dp.include_router(orders.router)
    dp.include_router(profile.router)
    dp.include_router(referrals.router)
    dp.include_router(promo.router)
    dp.include_router(support.router)
    dp.include_router(admin.router)

    await on_startup()
    autocheck = asyncio.create_task(payment_service.autocheck_loop(_bot))
    logger.info("Bot started")
    try:
        await dp.start_polling(_bot)
    finally:
        autocheck.cancel()
        await _bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger("bot").info("Bot stopped")

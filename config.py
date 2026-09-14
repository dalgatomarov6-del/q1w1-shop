"""Application configuration loaded from environment variables."""
import logging
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _parse_admin_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for item in raw.replace(" ", "").split(","):
        if not item:
            continue
        try:
            ids.append(int(item))
        except ValueError:
            logger.warning("Ignoring invalid ADMIN_IDS value: %r", item)
    return ids


@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: list[int] = field(default_factory=lambda: _parse_admin_ids(
        os.getenv("ADMIN_IDS", "")
    ))

    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.db")

    # Platega merchant credentials (https://docs.platega.io):
    # MERCHANT_ID — UUID мерчанта, SECRET — API-ключ (PLATEGA_API_KEY —
    # алиас для удобства). Ключ метода оплаты: 2 = СБП/QR, 10 = CardRu (МИР),
    # 12 = International. URL-адреса возврата необязательны.
    platega_merchant_id: str = os.getenv("PLATEGA_MERCHANT_ID", "")
    platega_secret: str = os.getenv("PLATEGA_SECRET") or os.getenv("PLATEGA_API_KEY", "")
    platega_api_url: str = os.getenv("PLATEGA_API_URL", "https://app.platega.io")
    platega_payment_method: int = int(os.getenv("PLATEGA_PAYMENT_METHOD", "2") or "2")
    platega_return_url: str = os.getenv("PLATEGA_RETURN_URL", "")
    platega_failed_url: str = os.getenv("PLATEGA_FAILED_URL", "")

    main_channel: str = os.getenv("MAIN_CHANNEL", "")
    support_username: str = os.getenv("SUPPORT_USERNAME", "")
    pubg_lookup_token: str = os.getenv("PUBG_LOOKUP_TOKEN", "")

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids


config = Config()

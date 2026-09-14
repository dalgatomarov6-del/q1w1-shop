# Milka Shop — Telegram Bot

A production-ready Telegram bot for a Metro Royale gaming service marketplace:
services (Metro Royale Escort with 5M–50M currency packages and custom amounts),
an items shop fully managed from the admin panel, Platega payments, promo codes,
a referral program, support tickets, colored buttons (Bot API 9.4) and a complete
admin panel for two admins.

## Stack

- Python 3.11+, aiogram 3.x (fully async)
- SQLite via SQLAlchemy 2.0 (async, `aiosqlite`)
- httpx for the Platega payment API (official: `X-MerchantId` / `X-Secret`,
  `POST /transaction/process`, `GET /transaction/{id}`)
- python-dotenv, Pillow (banner/product images)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your credentials
python bot.py
```

Deployment to a VPS (Ubuntu + systemd): see **[DEPLOY_VPS.md](DEPLOY_VPS.md)**.

### Environment variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `ADMIN_IDS` | Comma-separated Telegram user IDs (e.g. `8112037106,5503338424`) |
| `PLATEGA_MERCHANT_ID` / `PLATEGA_API_KEY` | Platega merchant UUID + API key (dashboard → Настройки → API). `PLATEGA_SECRET` is accepted as an alias |
| `PLATEGA_API_URL` | Default `https://app.platega.io` |
| `PLATEGA_PAYMENT_METHOD` | `2` = СБП/QR, `10` = CardRu (МИР), `12` = International |
| `PLATEGA_RETURN_URL` / `PLATEGA_FAILED_URL` | Optional redirect URLs after payment |
| `DATABASE_URL` | Defaults to local SQLite |
| `MAIN_CHANNEL` | Main channel @username or URL (menu button) |
| `SUPPORT_USERNAME` | Optional direct contact shown in the support section |

## Features

**Customer flow:** banner main menu with colored buttons → 🛍️ Магазин
(photo page) → Сопровождения (price table with interpolation for custom amounts)
or Товары → game ID → optional promo code → Platega invoice → payment
confirmation. Support section creates tickets (problem type + urgency + text)
that go straight to all admins; replies from admins are delivered in-bot.

**Colored buttons (Bot API 9.4):** `InlineKeyboardButton.style` — money/purchase
buttons are `success` (green), promo/support/info/referral are `primary`
(Telegram currently offers only red/green/blue; the "yellow" group maps to
primary — one constant `YELLOW_STYLE` in `keyboards/common.py`), destructive
actions are `danger` (red).

**Payments:** official Platega merchant API (`services/payments.py`); an order
is marked paid **only** after server-side status verification (CONFIRMED).
Manual "Check payment" button plus a background polling task; duplicate
confirmations are ignored.

**Admin panel** (`/admin`, both ADMIN_IDS): users with pagination, full cards
(ID, username, spent, last purchases, DM link), block/unblock; orders with
manual status changes (notifies the customer); transactions; statistics with
latest purchases; **tickets** (list/open/all, reply through the bot, close);
**accompaniment price editor** (tap a price point, add/remove points); product
CRUD with image uploads; promo code CRUD; broadcast (photo+text); runtime
settings — price table, min/max custom amounts, referral rewards, shop
open/closed, welcome/info/privacy texts.

**Referral program:** personal `?start=ref_<id>` links, self-referral and
duplicate protection, configurable reward.

## Project layout

```
bot.py                 # entrypoint: dispatcher, middlewares, payment wiring
config.py              # env-driven configuration
database/              # models, engine, all queries (incl. tickets)
handlers/              # start, shop, payments, orders, profile, referrals, promo, support, admin
keyboards/             # main menu, shop, support, admin keyboards (colored styles)
middlewares.py         # DB session + user injection
states.py              # FSM states
services/              # pricing engine, Platega client, order notifications
assets/                # banner + shop page images (shop/services/items.png) + uploads
deploy/                # systemd unit for VPS
DEPLOY_VPS.md          # пошаговая инструкция по загрузке на VPS
```

## Notes

- Timestamps are stored in UTC.
- Ticket tables are created automatically on first start (`create_all`).
- Page images are optional: if `assets/shop.png` / `services.png` / `items.png`
  are missing, the bot falls back to text pages. Replace the placeholders with
  your own artwork.
- Old inline buttons, stale products and expired payments are handled gracefully;
  errors are logged without ever logging credentials.

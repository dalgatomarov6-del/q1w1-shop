# 🚀 Milka Shop Bot — загрузка на VPS (полный туториал)

Команды для **Ubuntu 20.04/22.04/24.04**. Домен и SSL **не нужны** — бот работает через polling.

> ⚠️ **ВАЖНО:** папка бота на сервере должна называться **`milka-bot`** — без пробелов и заглавных букв.
> Путь с пробелом (`Milka Shop Bot`) ломает автозапуск systemd (ошибка `203/EXEC`).

---

## Шаг 1. Подключаемся к серверу

Своего компьютера (Windows PowerShell):

```bash
ssh root@ВАШ_IP
```

Вводим пароль от VPS (из письма хостинга). Появится строка `root@имя:~#` — вы на сервере.

---

## Шаг 2. Обновляем сервер и ставим пакеты

```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip nano software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv
python3.11 --version    # должно показать Python 3.11.x
```

> deadsnakes нужен на Ubuntu 20.04 (там системный Python 3.8 — слишком старый, бот требует 3.10+). На 22.04/24.04 тоже безвреден.

---

## Шаг 3. Создаём пользователя для бота

```bash
adduser milka              # придумать пароль, остальное — Enter
usermod -aG sudo milka
su - milka                 # дальше работаем под milka
```

> Если пользователь уже создан — пропустите этот шаг.
> Пароль sudo = пароль пользователя milka (при вводе символы не отображаются — это нормально).

---

## Шаг 4. Загружаем файлы бота на сервер

**Вариант А — со своего компьютера (PowerShell, НЕ на сервере!):**

```powershell
scp -r "C:\Users\Amin\Desktop\Milka Shop Bot" milka@ВАШ_IP:"/home/milka/"
```

**Вариант Б — мышкой:** программа WinSCP → подключиться (IP, логин milka, пароль) → перетащить папку в `/home/milka/`.

Теперь **переименовываем** папку (убираем пробел):

```bash
mv "/home/milka/Milka Shop Bot" /home/milka/milka-bot
ls /home/milka/milka-bot     # видим bot.py, handlers/, assets/, .env и т.д.
```

> Файл `database.db` можно не заливать — чистая база создастся сама при первом запуске.
> `.env` заливается вместе с папкой — токен и админы уже внутри.

---

## Шаг 5. Заполняем .env

```bash
cd /home/milka/milka-bot
nano .env
```

Проверяем/заполняем:

```ini
BOT_TOKEN=токен_от_BotFather
ADMIN_IDS=8112037106,5503338424

PLATEGA_MERCHANT_ID=UUID_мерчанта_из_панели_Platega
PLATEGA_API_KEY=секретный_ключ_из_панели_Platega
PLATEGA_API_URL=https://app.platega.io
PLATEGA_PAYMENT_METHOD=2
```

Сохранение в nano: **Ctrl+O → Enter → Ctrl+X**.

> Ключи Platega: панель Platega → «Настройки» → API. `PLATEGA_PAYMENT_METHOD`: 2 = СБП/QR, 10 = карта МИР, 12 = international.

---

## Шаг 6. Зависимости (виртуальное окружение)

```bash
cd /home/milka/milka-bot
rm -rf venv                       # пересоздаём, если venv делали на старом Python
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt   # ⚠️ дождаться конца! Не нажимать Ctrl+C
```

Проверочный запуск:

```bash
python bot.py
```

В консоли должно появиться `Bot started`. Откройте бота в Telegram → `/start` → покликать меню. Работает? Останавливаем: **Ctrl+C** и переходим к автозапуску.

---

## Шаг 7. Автозапуск 24/7 (systemd)

```bash
sudo cp /home/milka/milka-bot/deploy/milka-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now milka-bot
sudo systemctl status milka-bot    # должно быть: Active: active (running)
```

В файле `deploy/milka-bot.service` уже прописаны правильные пути (`/home/milka/milka-bot`) — ничего править не нужно, если делали по инструкции.

Готово — бот работает, сам поднимется после перезагрузки VPS и сам перезапустится при падении.

---

## Шаг 8. Логи и управление

```bash
journalctl -u milka-bot -f          # живые логи (выход Ctrl+C)
journalctl -u milka-bot -n 100      # последние 100 строк
sudo systemctl restart milka-bot    # перезапуск
sudo systemctl stop milka-bot       # остановить
```

---

## Обновление кода на сервере

1. Залить изменённые файлы (scp/WinSCP), **не перетирая** `.env` и `database.db`.
2. Если менялся `requirements.txt`:
   ```bash
   cd /home/milka/milka-bot && source venv/bin/activate && pip install -r requirements.txt
   ```
3. `sudo systemctl restart milka-bot`

---

## Бэкап базы (всё в одном файле database.db)

```bash
mkdir -p /home/milka/backups
cp /home/milka/milka-bot/database.db /home/milka/backups/db_$(date +%F).db
```

Автоматический бэкап каждый день в 4:00:

```bash
crontab -e
# добавить строку:
0 4 * * * cp /home/milka/milka-bot/database.db /home/milka/backups/db_$(date +\%F).db
```

---

## Частые проблемы

| Симптом | Причина и решение |
|---|---|
| `status=203/EXEC`, `Failed at step EXEC spawning /home/milka/Milka` | Пробел в пути. Папка должна быть `/home/milka/milka-bot`. Переименовать (`mv`), перепроверить пути в сервисе, `sudo systemctl daemon-reload && sudo systemctl restart milka-bot` |
| `TypeError: unsupported operand type(s) for \|` при запуске | Python слишком старый (3.8 на Ubuntu 20.04). Установить Python 3.11 (шаг 2) и пересоздать venv (шаг 6) |
| `status: failed` | Смотреть лог: `journalctl -u milka-bot -n 50`. Чаще всего опечатка в `.env` |
| pip установил не всё / оборвался | Запустить `pip install -r requirements.txt` ещё раз и дождаться конца |
| `Conflict: terminated by other getUpdates request` | Бот запущен в двух местах (сервер + ПК через start.bat). Остановить второй экземпляр |
| «Платёжная система недоступна» | Не заполнены `PLATEGA_MERCHANT_ID` / `PLATEGA_API_KEY` в `.env`, либо неверный `PLATEGA_API_URL` |
| Оплата создана, но не подтверждается | Проверить `PLATEGA_PAYMENT_METHOD` (2 = СБП) и оплату в панели Platega; бот проверяет статус кнопкой «🔄 Проверить оплату» и автоматически раз в минуту |
| Тикет не пришёл админу | Админ должен хотя бы раз нажать /start у бота — Telegram запрещает ботам писать первыми |
| Картинки магазина не показываются | Файлы `assets/shop.png`, `services.png`, `items.png` должны быть на сервере (переезжают вместе с папкой) |

---

## Безопасность

- `.env` никому не показывать и не коммитить в git.
- SSH: по возможности отключить root-логин и пароли (`sudo nano /etc/ssh/sshd_config` → `PermitRootLogin no`, `PasswordAuthentication no` → `sudo systemctl restart ssh`).
- Раз в пару недель: `sudo apt update && sudo apt upgrade -y`.
- Ubuntu 20.04 достигла конца поддержки — при возможности обновиться до 22.04 (`do-release-upgrade`), но это не блокирует работу бота.

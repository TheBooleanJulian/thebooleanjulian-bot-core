# thebooleanjulian-bot-core

> Shared library for all [TheBooleanJulian](https://github.com/TheBooleanJulian) Telegram bots.
> Branding · UI · Middleware · Status pages — one package, every bot.

---

## Install

Add to any bot's `requirements.txt`:

```
git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@main
```

Pin a release tag for stability:

```
git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@v1.0.0
```

---

## Modules

| Module | What it gives you |
|---|---|
| `branding` | Palette constants, message formatters (`fmt_success`, `fmt_error`, etc.) |
| `utils` | SGT timezone helpers, uptime tracking, text utilities |
| `middleware` | `rate_limit` decorator, `admin_only` decorator, `setup_logging`, error handler |
| `ui` | `confirm_keyboard`, `paginated_keyboard`, `url_button_keyboard` |
| `health` | `StatusServer` — drop-in Flask status page + `/healthz` for Zeabur |

---

## Status Page

Each bot gets a beautiful, auto-refreshing dark-mode status page at `/`:

```python
from julian_bot_core.health import StatusServer
from julian_bot_core.utils import mark_start

mark_start()  # call before anything else to track uptime

server = StatusServer(
    bot_name             = "My Bot",
    bot_username         = "@mybothandle",
    bot_description      = "Does cool things.",
    bot_version          = "1.0.0",
    commands             = [("/start", "Begin"), ("/help", "Help")],
    get_subscriber_count = lambda: len(my_subscribers),  # optional
    get_extra_metrics    = lambda: {"Next run": "00:00 SGT"},  # optional
    icon_emoji           = "🤖",
    accent_color         = "#00d4c8",  # override per-bot
)
server.start(port=8080)
```

**Endpoints:**
- `GET /` — Status page (HTML, auto-refreshes every 30s)
- `GET /healthz` — `{"status": "ok"}` for Zeabur health checks
- `GET /logs` — Last 100 log lines as JSON

---

## Quick start

```python
from julian_bot_core.middleware import setup_logging, rate_limit, global_error_handler
from julian_bot_core.branding import fmt_success, fmt_error, fmt_status_message
from julian_bot_core.utils import mark_start, fmt_uptime

logger = setup_logging("my-bot")
mark_start()

@rate_limit(calls=5, period=60)
async def my_handler(update, context):
    await update.message.reply_text(
        fmt_success("Done!", "Task completed."),
        parse_mode="HTML"
    )

# In your Application setup:
# application.add_error_handler(global_error_handler)
```

---

## Bots using this library

| Bot | Repo | Description |
|---|---|---|
| Miku Monday Bot | `itsmikumondaybot` | Weekly Miku GIFs to Telegram channels |
| MiguQuest Bot | `miguquestbot` | Gamified task manager, Miku-themed |
| NAC Busker Bot | `MikewNACBot` | Weekly busking schedule scraper |
| NASA APOD Bot | *(private)* | Daily astronomy picture cards |

---

## Versioning

Bump `version` in `setup.py` and tag a release when making breaking changes:

```bash
git tag v1.1.0
git push origin v1.1.0
```

---

*TheBooleanJulian · Built with ♪ and teal*

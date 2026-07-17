<div align="center">

# thebooleanjulian-bot-core

**Shared branding, middleware, UI helpers, and status pages for all TheBooleanJulian Telegram bots.**

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-00D4C8.svg)

</div>

---

## What it does

`thebooleanjulian-bot-core` is an internal shared library that provides common building blocks for every bot in the TheBooleanJulian fleet. Rather than duplicating branding constants, rate-limiting decorators, keyboard helpers, and status-page logic across repos, each bot installs this package and gets a consistent, maintainable foundation. It's not a standalone app — it's the shared core that bots pull in via `requirements.txt`.

## Features

- **Branding** — palette constants and message formatters (`fmt_success`, `fmt_error`, `fmt_status_message`)
- **Middleware** — `rate_limit` decorator, `admin_only` decorator, `setup_logging`, and a global error handler
- **UI helpers** — `confirm_keyboard`, `paginated_keyboard`, `url_button_keyboard`
- **Utils** — SGT timezone helpers, uptime tracking (`mark_start`, `fmt_uptime`), text utilities
- **Status server** — drop-in `StatusServer` (Flask) with a dark-mode auto-refreshing status page at `/`, `/healthz` for Zeabur health checks, and `/logs` for the last 100 log lines

## Modules

| Module | What it gives you |
|---|---|
| `branding` | Palette constants, message formatters |
| `utils` | SGT timezone helpers, uptime tracking, text utilities |
| `middleware` | `rate_limit`, `admin_only`, `setup_logging`, error handler |
| `ui` | `confirm_keyboard`, `paginated_keyboard`, `url_button_keyboard` |
| `health` | `StatusServer` — drop-in Flask status page + `/healthz` for Zeabur |

## Install

Add to any bot's `requirements.txt`:

```
git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@main
```

Pin a release tag for stability:

```
git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@v1.0.0
```

## Quick Start

```python
from julian_bot_core.middleware import setup_logging, rate_limit, global_error_handler
from julian_bot_core.branding import fmt_success, fmt_error
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

### Status Page

```python
from julian_bot_core.health import StatusServer
from julian_bot_core.utils import mark_start

mark_start()

server = StatusServer(
    bot_name             = "My Bot",
    bot_username         = "@mybothandle",
    bot_description      = "Does cool things.",
    bot_version          = "1.0.0",
    commands             = [("/start", "Begin"), ("/help", "Help")],
    get_subscriber_count = lambda: len(my_subscribers),  # optional
    get_extra_metrics    = lambda: {"Next run": "00:00 SGT"},  # optional
    icon_emoji           = "🤖",
    accent_color         = "#00d4c8",
)
server.start(port=8080)
```

**Endpoints:**
- `GET /` — Dark-mode status page, auto-refreshes every 30s
- `GET /healthz` — `{"status": "ok"}` for Zeabur health checks
- `GET /logs` — Last 100 log lines as JSON

## Project Structure

```
thebooleanjulian-bot-core/
|-- branding.py
|-- health.py
|-- middleware.py
|-- miku_monday_integration.py
|-- ui.py
|-- utils.py
|-- status_template.html
|-- status-page-preview.html
|-- setup.py
`-- __init__.py
```

## Versioning

Bump `version` in `setup.py` and tag a release when making breaking changes:

```bash
git tag v1.1.0
git push origin v1.1.0
```

## Bots Using This Library

| Bot | Repo | Description |
|---|---|---|
| Miku Monday Bot | `itsmikumondaybot` | Weekly Miku GIFs to Telegram channels |
| MiguQuest Bot | `miguquestbot` | Gamified task manager, Miku-themed |
| NAC Busker Bot | `MikewNACBot` | Weekly busking schedule scraper |
| NASA APOD Bot | *(private)* | Daily astronomy picture cards |

## Status / Roadmap

- [x] Core modules: branding, middleware, UI, utils, health
- [x] Drop-in `StatusServer` with Zeabur `/healthz` support
- [x] Miku Monday integration helper
- [ ] Publish to PyPI for cleaner installs

## Changelog

- **Early April 2026** — Renamed package from `julian-bot-core` to `thebooleanjulian-bot-core` across all files and references; initial public release with branding, middleware, UI, utils, and health modules

## License

MIT

---

<div align="center">
<sub>Built by <a href="https://github.com/TheBooleanJulian">@TheBooleanJulian</a></sub>
</div>
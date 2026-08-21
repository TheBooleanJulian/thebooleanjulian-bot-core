<div align="center">

# thebooleanjulian-bot-core

**Opt-in shared building blocks for TheBooleanJulian's Telegram bots — extracted from what the bots actually do, not designed top-down.**

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-00D4C8.svg)

</div>

---

## What it is (and isn't)

v1 of this package was written before any bot actually used it, and it showed: it mandated a Flask-based status server, but two real bots (openclaw, clawsune) had already dropped Flask on purpose to work around a Zeabur/uvicorn port-detection bug. It shipped a `pytz` dependency that nothing imported. Nine bots declared it in `requirements.txt`; zero imported anything from it.

v2 is a rewrite based on a survey of the actual bot codebases in this fleet. It's a **toolbox, not a bootstrap sequence** — every module is independent and opt-in. Some patterns (logging setup, admin gating, a health-check contract) really are common across bots and are worth sharing. Others (which HTTP server library, whether to fail-fast on Telegram's 409 Conflict, rate limiting, timezone handling) genuinely vary bot-to-bot for real deploy/product reasons, so this package offers multiple backends or leaves them fully optional instead of picking one and forcing it everywhere.

## Modules

| Module | What it gives you | Actually common? |
|---|---|---|
| `logging_setup` | `setup_logging()` — stdout handler, silences `httpx`/`httpcore` (they log request URLs, which include the bot token), optional rotating file, optional in-memory buffer for a status page | Yes — every real bot does some form of this |
| `admin` | `admin_only()` decorator, `AdminFilter`/`AllowedChatFilter` (BaseFilter), `is_admin()` | The *need* is universal; 3 different shapes exist in the wild, so this offers all of them rather than picking one |
| `health` | `SimpleStatusServer` (stdlib `http.server`, zero deps — the Zeabur-safe default) and `FlaskStatusServer` (needs the `flask` extra) — same constructor, same rendered page | Only the *contract* (`/`, `/healthz`) is common; the transport genuinely varies by deploy target |
| `error_handling` | `error_boundary()` (per-handler try/except + friendly reply), `make_error_handler()` (Application-level; `exit_on_conflict=True` opts into the openclaw/clawsune Zeabur fail-fast pattern) | Partially — friendly-error-card is common, fail-fast-on-Conflict is deploy-topology-specific |
| `ratelimit` | `rate_limit(calls, period, key)` — per-command token bucket | No — only one bot in the fleet actually needs this; kept fully optional |
| `branding` | Palette constants, `fmt_success`/`fmt_error`/`fmt_warn`/`fmt_status_message` | Cosmetic, zero side effects, safe to adopt piecemeal |
| `utils` | SGT helpers, `mark_start()`/`fmt_uptime()`, `truncate()`, `plural()` | Only relevant if a bot schedules things or shows uptime — several bots have no timezone need at all |
| `ui` | `InlineKeyboardMarkup` builders (`confirm_keyboard`, `paginated_keyboard`, ...) | Generic PTB helpers, opt-in |

## Install

```
# Base (stdlib status server only)
git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@main

# With Flask status server support
git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@main#egg=thebooleanjulian-bot-core[flask]
```

**Track `@main`, don't pin a tag.** The fleet's whole point is one core update reaching every bot — see "Fleet propagation" below. Pin to a tag only for a deliberate, temporary freeze (e.g. investigating a regression), and unpin once you're done.

## Fleet propagation

Every push to this repo's `main` branch triggers `.github/workflows/propagate.yml`:

1. Redeploys **[bot-core-canary](https://github.com/TheBooleanJulian/bot-core-canary)** — a throwaway service with no real users whose only job is to import bot-core and stay healthy.
2. Polls its `/healthz`. If it doesn't come up healthy, the pipeline **stops here** — nothing else is touched, and the workflow fails loudly in GitHub Actions.
3. Only if the canary is healthy does it fan out redeploys to every service listed in `deploy/fleet.json`.

This is why bots should track `@main` instead of pinning: they're not expected to manually bump a version. bot-core pushes, the canary catches anything broken before it reaches a real bot, and everything else picks it up within minutes of that push.

Redeploys go through **Zeabur's GraphQL API** (`redeployService` mutation), not a webhook — Zeabur has no deploy-trigger webhook feature (confirmed against their Apollo Explorer schema; it's a requested feature, not shipped). One account-wide `ZEABUR_API_TOKEN` secret authenticates every service's redeploy call.

**Adding a new bot/webapp to the fleet:**
1. Get its Zeabur `serviceID` and `environmentID` (from the Zeabur GraphQL API/Apollo Explorer — these are identifiers, not secrets, safe to commit).
2. Add an entry to `deploy/fleet.json` (`name`, `repo`, `service_id`, `environment_id`, `health_url`).

That's it — no new secret, no workflow YAML edit. One `ZEABUR_API_TOKEN` covers the whole fleet.

## Quick start

Pick whichever pieces fit. Two full worked examples matching real bot shapes are in [`examples/`](examples/):

- [`zeabur_stdlib_bot.py`](examples/zeabur_stdlib_bot.py) — single-owner bot on Zeabur, stdlib status server, fail-fast on Conflict (openclaw/clawsune's actual shape)
- [`community_flask_bot.py`](examples/community_flask_bot.py) — owner + community command tiers, rate limiting, Flask status server (monitoring-miku's actual shape)

Minimal:

```python
from thebooleanjulian_bot_core.logging_setup import setup_logging
from thebooleanjulian_bot_core.admin import admin_only
from thebooleanjulian_bot_core.health import StatusServer  # stdlib backend
from thebooleanjulian_bot_core.utils import mark_start

setup_logging()
mark_start()

server = StatusServer(
    bot_name="My Bot",
    bot_username="@mybothandle",
    bot_description="Does one thing well.",
    commands=[("/start", "Wake up")],
    get_metrics=lambda: {"Subscribers": len(subscribers)},
)
server.start()  # binds $PORT or 8080

@admin_only(OWNER_ID)  # silent for non-owners, matching every real bot's behaviour
async def status_handler(update, context): ...
```

**Endpoints (both backends):** `GET /` status page, `GET /healthz` → `{"status": "ok"}`, `GET /logs` → last 100 buffered lines (only populated if `setup_logging(buffer=True)`).

## Bots using this library

| Service | Tracks | Notes |
|---|---|---|
| `bot-core-canary` | `@main` | Canary — gates fleet propagation, no real users |
| `clawsune` | `@main` | First real integration: `setup_logging`, `admin_only`, `error_handling` |

v1 was declared as a dependency in 9 repos' `requirements.txt` but never actually imported by any of them — don't add a bot to this table speculatively; add it when it actually imports something and is registered in `deploy/fleet.json`.

## Fleet survey (why the API looks like this)

Real Python Telegram bots found in this workspace, as of this rewrite: `openclaw`, `clawsune`, `miku-ocr`, `miku-singlish-word-of-the-day`, `mikuquest`, `monitoring-miku`, `ig-uwu-bot`, `mikew-gcal-v1`, `mikew-gcal-v3`, `accurova-loyalty/telegram_bot`. (Several other repos declare a Telegram-bot-shaped dependency but are actually Node.js, static sites, or non-bot tools — see git history / handover notes for the full exclusion list.)

`mikew-gcal-v3/health.py` had already independently built a generic Flask `StatusServer` explicitly to replace this package — its constructor shape is what `FlaskStatusServer` is modeled on.

## Versioning

Bump `version` in `setup.py` and tag a release on breaking changes:

```bash
git tag v2.0.0
git push origin v2.0.0
```

## Changelog

- **v2.1.0** — Added fleet-wide auto-propagation: `.github/workflows/propagate.yml` redeploys `bot-core-canary` on every push to `main`, gates on its `/healthz`, and only then fans out redeploys to `deploy/fleet.json`. Reverted the "pin a tag" install guidance — bots should track `@main` now that a canary catches breakage before it reaches them.
- **v2.0.0** — Rewrite from a bottom-up survey of the actual bot fleet. Replaced the Flask-only `StatusServer` with two interchangeable backends (stdlib default + optional Flask). Split `middleware.py` into `logging_setup`, `admin`, `ratelimit`, `error_handling` — each independent and opt-in, mirroring the real shapes found (inline checks, filter classes, per-command rate limits, conflict-fail-fast vs. friendly-error-card). Dropped the unused `pytz` dependency. Removed the fabricated "Bots Using This Library" table (none of those bots existed or imported this package) and the stale Miku Monday integration example (that bot turned out to be Node.js).
- **v1.0.0** — Initial release: branding, middleware (rate_limit, admin_only, setup_logging, global error handler), UI helpers, utils, Flask-based health server. Written speculatively before any bot integrated it.

## License

MIT

---

<div align="center">
<sub>Built by <a href="https://github.com/TheBooleanJulian">@TheBooleanJulian</a></sub>
</div>

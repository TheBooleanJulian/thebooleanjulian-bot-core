# Handover — thebooleanjulian-bot-core

_Last updated: 2026-08-21_

## Current state

v2.0.0 is live on `main` and tagged. It's a bottom-up rewrite, based on
actually reading the real bot fleet's code (9 real Python Telegram bots
found across the workspace) instead of the top-down guesswork v1 was.

Modules: `logging_setup`, `admin`, `ratelimit`, `error_handling`, `health`
(two backends: `SimpleStatusServer` stdlib-default, `FlaskStatusServer`
opt-in via the `flask` extra), `branding`, `utils`, `ui`. All independent
and opt-in — nothing requires a specific bootstrap sequence.

Every module was exercised with real async handler calls (not just
import checks) before anything was committed. One real bug was caught
and fixed in the process: `_BufferHandler.emit()` called `formatTime()`
on a `logging.Handler`, which doesn't have that method — it's a
`Formatter` method. This was in v1 too, silently, since nothing ever
exercised the log buffer.

`clawsune` is the first real bot integration (v1.4.1, pinned to
bot-core `v2.0.0`): `setup_logging()`, `@admin_only` on owner-gated
commands, `make_error_handler(exit_on_conflict=True)`. Its custom
status page (`web.py`, stdlib `http.server`, memory-aware) was
deliberately left alone — bot-core's Flask backend would reintroduce
the exact Zeabur/uvicorn bug clawsune's own changelog says it fixed.

## What changed (v1 → v2)

- `middleware.py` (rate_limit + admin_only + setup_logging + one global
  error handler, all bundled) → split into `logging_setup.py`,
  `admin.py`, `ratelimit.py`, `error_handling.py`
- `health.StatusServer` (Flask-only, mandatory) → `health.SimpleStatusServer`
  (stdlib, zero deps, now default) + `health.FlaskStatusServer` (opt-in),
  sharing one HTML renderer (`health/render.py`)
- Dropped unused `pytz` dependency
- Removed the fabricated "Bots Using This Library" table and the stale
  Miku Monday integration example (that bot turned out to be Node.js)
- Added two worked examples in `examples/` matching real bot shapes

## Open questions / not done

- **8 other bots** still declare bot-core in `requirements.txt` but
  don't import it (`luxsync-v2`, `food-analyst-bot`, `followtrain-v2`,
  `retouch-relay`, `stark-db`, `pixiv-organiser`, `openclaw`,
  `miku-monday`). Some of those `requirements.txt` entries are dead
  (repo isn't even Python, e.g. `miku-monday`, `stark-db`,
  `pixiv-organiser`, `food-analyst-bot`) and should probably just be
  deleted from those files rather than "integrated."
- `openclaw` is the closest real candidate for a second integration —
  same shape as clawsune (they're siblings), should be a near-identical
  diff.
- `mikew-gcal-v3/health.py` has its own generic Flask `StatusServer`
  (the reference `FlaskStatusServer` was modeled on) — not yet migrated
  to import from bot-core; still has its own local copy.
- `thebooleanjulian-webapp-core` (a sibling package for the FastAPI
  apps — accurova-card, accurova-live-event, accurova-loyalty,
  probe-seo-analyzer, repo-tracker, rothko-cal) is being scoped out
  separately; not started as of this handover.
- No CI/test suite in this repo — all validation so far has been ad hoc
  (smoke-tested locally, not automated). Worth adding if more bots
  start depending on this.

## Not attempted this session (needs explicit scope/authorization)

`good-practices.md`'s security items — "No secrets in code" audit across
15+ bots sharing this package, key rotation scheduling, least-privilege
credential review — were not run as part of this rewrite. They're
fleet-wide, credential-touching operations that deserve their own
explicitly-scoped pass, not something to fold into a library rewrite.

"""
TheBooleanJulian Bot Core — Middleware
=======================================
Decorators and handlers for rate-limiting, admin access guards,
and a standardised logging config shared by all bots.
"""

import logging
import functools
import time
from collections import defaultdict
from typing import Callable, Optional

from .branding import fmt_warn, fmt_error

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# In-memory circular log buffer (last N lines), used by the status page
_log_buffer: list[dict] = []
_LOG_BUFFER_MAX = 200

class _BufferHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        _log_buffer.append({
            "time":    self.formatTime(record, DATE_FORMAT),
            "level":   record.levelname,
            "name":    record.name,
            "message": record.getMessage(),
        })
        if len(_log_buffer) > _LOG_BUFFER_MAX:
            _log_buffer.pop(0)

def setup_logging(bot_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure a logger for a bot.
    Returns the root logger; use logging.getLogger(__name__) in submodules.
    """
    root = logging.getLogger()
    root.setLevel(level)

    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        root.addHandler(sh)

    if not any(isinstance(h, _BufferHandler) for h in root.handlers):
        bh = _BufferHandler()
        root.addHandler(bh)

    return logging.getLogger(bot_name)

def get_log_buffer(n: int = 50) -> list[dict]:
    """Return the last n log entries for the status page."""
    return list(reversed(_log_buffer[-n:]))


# ── Rate limiting ─────────────────────────────────────────────────────────────

_rate_store: dict[int, list[float]] = defaultdict(list)

def rate_limit(calls: int = 5, period: int = 60):
    """
    Decorator for python-telegram-bot handlers.
    Limits each user to `calls` per `period` seconds.

    Usage:
        @rate_limit(calls=3, period=30)
        async def my_handler(update, context): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            now = time.monotonic()
            timestamps = _rate_store[user_id]
            # Purge old timestamps
            _rate_store[user_id] = [t for t in timestamps if now - t < period]
            if len(_rate_store[user_id]) >= calls:
                await update.effective_message.reply_text(
                    fmt_warn("Slow down!", f"Max {calls} requests per {period}s."),
                    parse_mode="HTML"
                )
                return
            _rate_store[user_id].append(now)
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator


# ── Admin guard ───────────────────────────────────────────────────────────────

def admin_only(admin_ids: Optional[list[int]] = None):
    """
    Decorator that restricts a handler to admin user IDs.
    IDs can be passed in, or read from context.bot_data['admin_ids'].

    Usage:
        @admin_only([123456789])
        async def secret_handler(update, context): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            ids = admin_ids or context.bot_data.get("admin_ids", [])
            user_id = update.effective_user.id
            if ids and user_id not in ids:
                await update.effective_message.reply_text(
                    fmt_error("Access denied.", "This command is for admins only."),
                    parse_mode="HTML"
                )
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator


# ── Error handler ─────────────────────────────────────────────────────────────

async def global_error_handler(update, context) -> None:
    """
    Attach to the Application as an error handler.
    Logs the exception and optionally notifies the user.
    """
    logger = logging.getLogger("bot.error")
    logger.error("Unhandled exception", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            fmt_error("Something went wrong.", "The dev has been notified."),
            parse_mode="HTML"
        )

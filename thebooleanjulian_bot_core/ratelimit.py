"""
TheBooleanJulian Bot Core — Rate Limiting
============================================
Opt-in. Only one bot in the fleet (monitoring-miku) actually rate-limits
today — most are single-owner bots with no abuse surface. This is that
bot's real per-command token-bucket, generalised.
"""

import functools
import logging
import time
from collections import defaultdict
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# { (user_id, key): [timestamp, ...] }
_call_log: dict[tuple, list[float]] = defaultdict(list)


def rate_limit(calls: int = 3, period: int = 10, key: Optional[str] = None):
    """
    Decorator factory for python-telegram-bot handlers. Limits each user to
    `calls` per `period` seconds, tracked separately per `key` (defaults to
    the wrapped function's name, so different commands don't share a bucket).

    Usage:
        @rate_limit(calls=1, period=15)   # expensive command
        async def debug_command(update, context): ...

        @rate_limit()   # default 3 per 10s
        async def status_command(update, context): ...
    """
    def decorator(func: Callable) -> Callable:
        bucket_key = key or func.__name__

        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            user_id = user.id if user else 0
            store_key = (user_id, bucket_key)
            now = time.monotonic()

            _call_log[store_key] = [t for t in _call_log[store_key] if now - t < period]

            if len(_call_log[store_key]) >= calls:
                oldest = _call_log[store_key][0]
                wait = int(period - (now - oldest)) + 1
                logger.info("[rate_limit] user=%s key=%s throttled, retry in %ss", user_id, bucket_key, wait)
                await update.effective_message.reply_text(
                    f"⏳ Slow down — retry in {wait}s.",
                )
                return

            _call_log[store_key].append(now)
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

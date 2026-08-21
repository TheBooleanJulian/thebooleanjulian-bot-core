"""
TheBooleanJulian Bot Core — Error Handling
=============================================
Two real, independent patterns exist in the fleet and neither subsumes
the other, so both are exposed separately:

  1. Fail-fast on Telegram 409 Conflict (openclaw, clawsune). Zeabur runs
     one instance; a 409 means an orphaned duplicate poller is still up.
     Exiting immediately lets the platform's restart policy replace it
     cleanly instead of retry-looping forever alongside the real instance.

  2. A friendly error card + traceback log for everything else
     (monitoring-miku), as a per-handler decorator and/or an
     Application-level catch-all — never leaks internals to the chat.

Compose what you need with make_error_handler(); most bots only need
one or the other, not both.
"""

import functools
import logging
import traceback
from typing import Callable, Optional

logger = logging.getLogger(__name__)

DEFAULT_FRIENDLY_MESSAGE = (
    "⚠️ Something went wrong.\n"
    "The error has been logged. If it persists, try again shortly."
)


def error_boundary(friendly_message: str = DEFAULT_FRIENDLY_MESSAGE):
    """
    Per-handler try/except. Catches exceptions raised inside a single
    handler, logs the traceback, and replies with a friendly message
    instead of letting the update silently fail.

    Usage:
        @error_boundary()
        async def my_command(update, context): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)
            except Exception:
                logger.error("[error_boundary] unhandled exception in %s:\n%s",
                             func.__name__, traceback.format_exc())
                if update and getattr(update, "effective_message", None):
                    try:
                        await update.effective_message.reply_text(friendly_message)
                    except Exception:
                        pass  # don't let the error handler crash too
        return wrapper
    return decorator


def make_error_handler(
    *,
    exit_on_conflict: bool = False,
    notify_user: bool = False,
    friendly_message: str = DEFAULT_FRIENDLY_MESSAGE,
):
    """
    Builds an Application-level error handler (register with
    `application.add_error_handler(handler)`).

    exit_on_conflict: os._exit(1) on Telegram's 409 Conflict — the
                       openclaw/clawsune Zeabur single-poller pattern.
                       Only enable this if your deploy target restarts
                       failed processes automatically.
    notify_user:       reply to the user with friendly_message on any
                        other unhandled error. Off by default — most
                        bots in the fleet just log and move on.
    """
    async def handler(update, context) -> None:
        error = context.error

        if exit_on_conflict:
            try:
                from telegram.error import Conflict
                if isinstance(error, Conflict):
                    logger.critical(
                        "Telegram 409 Conflict: another instance is already polling "
                        "this bot token. Exiting so this duplicate process fails fast."
                    )
                    import os
                    os._exit(1)
            except ImportError:
                pass

        logger.error("[global_error_handler] unhandled error: %s\n%s",
                     error, "".join(traceback.format_exception(type(error), error, error.__traceback__)) if error else "")

        if notify_user and update and getattr(update, "effective_message", None):
            try:
                await update.effective_message.reply_text(friendly_message)
            except Exception:
                pass

    return handler

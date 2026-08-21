"""
TheBooleanJulian Bot Core — Admin / Access Control
=====================================================
Every bot in the fleet gates commands by user ID, but no two do it the
same way: inline `if user_id != OWNER_ID` checks (openclaw, clawsune),
a filter class + decorator two-tier model (monitoring-miku), or a set +
helper function (mikew-gcal-v3). This module gives you the pieces to
build any of those shapes instead of picking one for you.

Note on silence: every real owner-only bot in the fleet drops
unauthorised messages *silently* — no "access denied" reply — so a
stranger DMing the bot gets no signal it's owner-gated. That's the
default here. Pass reply=fmt_error(...) if you want monitoring-miku's
audit-log-only behaviour to instead notify the caller.
"""

import functools
import logging
from typing import Callable, Iterable, Optional, Union

logger = logging.getLogger(__name__)

IdsArg = Union[int, Iterable[int], Callable[[], Iterable[int]]]


def _resolve_ids(ids: IdsArg) -> set:
    if callable(ids):
        ids = ids()
    if isinstance(ids, int):
        return {ids}
    return set(ids)


def is_admin(user_id: int, admin_ids: IdsArg) -> bool:
    return user_id in _resolve_ids(admin_ids)


def admin_only(admin_ids: IdsArg, *, reply: Optional[str] = None, parse_mode: str = "HTML"):
    """
    Decorator restricting a python-telegram-bot handler to specific user IDs.

    admin_ids: an int, a collection of ints, or a zero-arg callable returning
               one (so you can pass a function that reads live config instead
               of a value captured at import time).
    reply:     if given, sent back to unauthorised callers. Default is silent
               (matches openclaw/clawsune/monitoring-miku's actual behaviour).

    Usage:
        @admin_only(OWNER_ID)
        async def secret_handler(update, context): ...

        @admin_only(lambda: config.ADMIN_IDS)
        async def secret_handler(update, context): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            user_id = user.id if user else None
            if user_id is None or not is_admin(user_id, admin_ids):
                logger.warning(
                    "[admin_only] blocked user_id=%s from %s", user_id, func.__name__
                )
                if reply:
                    await update.effective_message.reply_text(reply, parse_mode=parse_mode)
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator


try:
    from telegram.ext import filters as _tg_filters

    class AdminFilter(_tg_filters.BaseFilter):
        """
        BaseFilter counterpart to admin_only, for registering at the
        CommandHandler level (monitoring-miku's owner_filter pattern) rather
        than inside the handler body. Combine both for belt-and-suspenders.
        """
        def __init__(self, admin_ids: IdsArg):
            super().__init__()
            self._admin_ids = admin_ids

        def filter(self, message) -> bool:
            user = message.from_user
            return user is not None and is_admin(user.id, self._admin_ids)


    class AllowedChatFilter(_tg_filters.BaseFilter):
        """
        Passes for messages from a fixed set of chat IDs — for bots that
        want commands usable in curated groups/channels as well as DMs
        (monitoring-miku's community_filter pattern), as opposed to
        AdminFilter's per-user identity check.
        """
        def __init__(self, chat_ids: IdsArg):
            super().__init__()
            self._chat_ids = chat_ids

        def filter(self, message) -> bool:
            return message.chat_id in _resolve_ids(self._chat_ids)

except ImportError:
    pass

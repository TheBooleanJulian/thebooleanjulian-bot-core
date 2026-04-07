"""
julian-bot-core
================
Shared library for all TheBooleanJulian Telegram bots.

Quick start:

    from julian_bot_core.branding import fmt_success, fmt_error
    from julian_bot_core.utils import now_sgt, fmt_uptime, mark_start
    from julian_bot_core.middleware import setup_logging, rate_limit, admin_only
    from julian_bot_core.health import StatusServer
    from julian_bot_core.ui import confirm_keyboard, paginated_keyboard
"""

from .branding  import *          # noqa: F401,F403
from .utils     import mark_start # noqa: F401
from .middleware import setup_logging, global_error_handler  # noqa: F401

__version__ = "1.0.0"
__author__  = "TheBooleanJulian"

"""
thebooleanjulian-bot-core
================
Shared, opt-in building blocks for TheBooleanJulian's Telegram bots.

Nothing here is a required bootstrap sequence — pull in only the pieces
a given bot actually needs. Modules:

    logging_setup   setup_logging() — stdout + optional rotating file,
                     silences httpx/httpcore (they log the bot token)
    admin           admin_only() decorator, AdminFilter/AllowedChatFilter,
                     is_admin() — three shapes of the same access check
    ratelimit       rate_limit() — opt-in per-command token bucket
    error_handling  error_boundary() (per-handler), make_error_handler()
                     (Application-level; conflict-fail-fast is opt-in)
    health          SimpleStatusServer (stdlib, Zeabur-safe) or
                     FlaskStatusServer (needs the `flask` extra)
    branding        palette constants, fmt_success/fmt_error/... formatters
    utils           SGT helpers, mark_start()/fmt_uptime(), text helpers
    ui              InlineKeyboardMarkup builders

See README.md for which of these are actually common across the fleet
vs. genuinely bot-specific — don't force a pattern just because it's here.
"""

__version__ = "2.1.0"
__author__ = "TheBooleanJulian"

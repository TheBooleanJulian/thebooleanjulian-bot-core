"""
Example: Integrating thebooleanjulian-bot-core into the Miku Monday Bot
=============================================================
This shows the minimal changes needed to wire up core features.
Assumes you already have a working bot. Just replace the parts below.
"""

# ── requirements.txt addition ─────────────────────────────────────────────────
#
#   git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@main
#
# Or pin a version tag for stability:
#   git+https://github.com/TheBooleanJulian/thebooleanjulian-bot-core.git@v1.0.0

# ── main.py changes ───────────────────────────────────────────────────────────

from julian_bot_core.middleware import setup_logging, global_error_handler, rate_limit
from julian_bot_core.health import StatusServer
from julian_bot_core.branding import fmt_status_message, fmt_success, BRAND_FOOTER
from julian_bot_core.utils import mark_start, fmt_uptime, fmt_datetime, now_sgt

# 1. Setup logging (call before anything else)
logger = setup_logging("miku-monday")

# 2. Your subscriber set (or DB call)
subscribers: set = set()

def get_subscriber_count() -> int:
    return len(subscribers)

def get_extra_metrics() -> dict:
    # Any extra info to show on the status page
    next_monday = "Mon 09:00 SGT"  # replace with real calc
    return {
        "Next post": next_monday,
    }

# 3. Start the status server (before bot polling)
mark_start()

server = StatusServer(
    bot_name             = "Miku Monday Bot",
    bot_username         = "@itsmikumondaybot",
    bot_description      = "Spreading Hatsune Miku joy every Monday! ♪",
    bot_version          = "2.1.0",
    commands             = [
        ("/start",       "Welcome & register your channel"),
        ("/status",      "Show bot status & next post"),
        ("/countdown",   "Time until next Miku Monday"),
        ("/unsubscribe", "Remove this channel"),
        ("/feedback",    "Send feedback to the dev"),
    ],
    get_subscriber_count = get_subscriber_count,
    get_extra_metrics    = get_extra_metrics,
    icon_emoji           = "🎵",
    # accent_color defaults to #00d4c8 — fits perfectly for Miku
)
server.start(port=8080)

# 4. Apply rate_limit to any handler
# @rate_limit(calls=5, period=60)
# async def start_handler(update, context): ...

# 5. Register the global error handler on your Application
# application.add_error_handler(global_error_handler)

# 6. Use fmt_status_message in your /status command
# async def status_handler(update, context):
#     text = fmt_status_message(
#         bot_name = "Miku Monday Bot",
#         status   = "online",
#         fields   = {
#             "Uptime":      fmt_uptime(),
#             "Subscribers": str(get_subscriber_count()),
#             "Next Miku Monday": next_monday_str(),
#         }
#     )
#     await update.message.reply_text(text, parse_mode="HTML")

"""
Example: a multi-tier bot with owner-only ops commands and community
commands usable in curated groups/channels (monitoring-miku's real
shape), on a deploy target where Flask is fine. Adds rate limiting on
an expensive command, and a friendly (non-fail-fast) error card.

Install with the flask extra: pip install "thebooleanjulian-bot-core[flask]"
"""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from thebooleanjulian_bot_core.logging_setup import setup_logging
from thebooleanjulian_bot_core.admin import AdminFilter, AllowedChatFilter, admin_only
from thebooleanjulian_bot_core.ratelimit import rate_limit
from thebooleanjulian_bot_core.error_handling import make_error_handler
from thebooleanjulian_bot_core.health import FlaskStatusServer
from thebooleanjulian_bot_core.utils import mark_start

setup_logging(buffer=True)

BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_TELEGRAM_ID"])
ALLOWED_CHAT_IDS = {int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x}

owner_filter = AdminFilter(OWNER_ID)
community_filter = AllowedChatFilter(lambda: ALLOWED_CHAT_IDS | {OWNER_ID})


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("All systems nominal.")


@admin_only(OWNER_ID)
@rate_limit(calls=1, period=15)  # expensive — e.g. an LLM call
async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Debug report...")


def main():
    mark_start()

    server = FlaskStatusServer(
        bot_name="Community Bot",
        bot_username="@mycommunitybot",
        bot_description="Owner ops + community status commands.",
        commands=[("/status", "Community status"), ("/debug", "Owner-only debug report")],
    )
    server.start()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(make_error_handler(notify_user=True))
    app.add_handler(CommandHandler("status", status, filters=community_filter))
    app.add_handler(CommandHandler("debug", debug, filters=owner_filter))
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

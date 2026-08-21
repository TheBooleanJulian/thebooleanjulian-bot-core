"""
Example: a single-owner bot deployed on Zeabur (openclaw/clawsune's real shape).

Uses the stdlib-based SimpleStatusServer, not Flask — Zeabur's uvicorn
auto-detection misfires against a Flask app on this platform, which is
why those two bots dropped Flask entirely. Fail-fast on Telegram 409
Conflict so an orphaned duplicate poller doesn't idle forever next to
the real instance.
"""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from thebooleanjulian_bot_core.logging_setup import setup_logging
from thebooleanjulian_bot_core.admin import admin_only
from thebooleanjulian_bot_core.error_handling import make_error_handler
from thebooleanjulian_bot_core.health import StatusServer  # SimpleStatusServer
from thebooleanjulian_bot_core.utils import mark_start, fmt_uptime

setup_logging(buffer=True)  # buffer=True feeds the status page's log panel

BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_TELEGRAM_ID"])

subscribers: set = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Online.")


@admin_only(OWNER_ID)  # silent for non-owners, matching real bot behaviour
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Uptime: {fmt_uptime()}")


def main():
    mark_start()

    server = StatusServer(
        bot_name="My Bot",
        bot_username="@mybothandle",
        bot_description="Does one thing well.",
        commands=[("/start", "Wake up"), ("/status", "Owner-only status")],
        get_metrics=lambda: {"Subscribers": len(subscribers)},
        icon_emoji="🤖",
    )
    server.start()  # binds $PORT or 8080

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(make_error_handler(exit_on_conflict=True))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

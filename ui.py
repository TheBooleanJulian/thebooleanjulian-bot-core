"""
TheBooleanJulian Bot Core — UI
================================
Reusable InlineKeyboardMarkup builders and common message patterns
for all bots in the ecosystem.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Optional

# ── Button builders ───────────────────────────────────────────────────────────

def confirm_keyboard(
    confirm_data: str = "confirm",
    cancel_data: str  = "cancel",
    confirm_label: str = "✅ Confirm",
    cancel_label: str  = "❌ Cancel",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(confirm_label, callback_data=confirm_data),
        InlineKeyboardButton(cancel_label,  callback_data=cancel_data),
    ]])

def back_keyboard(
    back_data: str   = "back",
    back_label: str  = "← Back",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(back_label, callback_data=back_data)
    ]])

def url_button_keyboard(label: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, url=url)]])

def paginated_keyboard(
    items: list[tuple[str, str]],   # [(label, callback_data), ...]
    page: int = 0,
    page_size: int = 5,
    nav_prefix: str = "page",
) -> InlineKeyboardMarkup:
    """
    Builds a paginated inline keyboard with prev/next navigation.
    nav_prefix is prepended to callback_data for prev/next buttons.
    """
    start = page * page_size
    chunk = items[start : start + page_size]
    rows  = [[InlineKeyboardButton(label, callback_data=data)] for label, data in chunk]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ Prev", callback_data=f"{nav_prefix}:{page-1}"))
    if start + page_size < len(items):
        nav.append(InlineKeyboardButton("Next ▶", callback_data=f"{nav_prefix}:{page+1}"))
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(rows)


# ── Loading / placeholder messages ────────────────────────────────────────────

LOADING_MSG = "⏳ <i>Processing…</i>"
DONE_MSG    = "✅ Done."

async def send_loading(update, context) -> object:
    """Send a loading placeholder; returns the message object for later editing."""
    return await update.effective_message.reply_text(LOADING_MSG, parse_mode="HTML")

async def edit_to_result(message, text: str) -> None:
    """Replace a loading message with the final result."""
    await message.edit_text(text, parse_mode="HTML")

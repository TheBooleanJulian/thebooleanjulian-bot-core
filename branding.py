"""
TheBooleanJulian Bot Core — Branding
=====================================
Centralised brand constants, formatters, and message templates.
All bots in the TheBooleanJulian ecosystem share these.
"""

# ── Palette ──────────────────────────────────────────────────────────────────
TEAL       = "#00d4c8"
TEAL_DARK  = "#009e94"
BG_DARK    = "#060910"
BG_CARD    = "#0c1018"
TEXT_WHITE = "#e8eaf0"
TEXT_MUTED = "#6b7280"

# ── Identity ──────────────────────────────────────────────────────────────────
BRAND_NAME   = "TheBooleanJulian"
BRAND_HANDLE = "@JulianC97"
BRAND_GITHUB = "https://github.com/TheBooleanJulian"
BRAND_FOOTER = f"Built by {BRAND_NAME} · {BRAND_GITHUB}"

# ── Miku / Vocaloid emoji palette ─────────────────────────────────────────────
MIKU_SPARKLE = "✦"
MIKU_NOTE    = "♪"
MIKU_TEAL    = "🩵"
MIKU_STAR    = "🌟"

# ── Standard message emoji ────────────────────────────────────────────────────
EMOJI_OK      = "✅"
EMOJI_ERROR   = "❌"
EMOJI_WARN    = "⚠️"
EMOJI_INFO    = "💡"
EMOJI_LOADING = "⏳"
EMOJI_BOT     = "🤖"
EMOJI_CLOCK   = "🕐"
EMOJI_USERS   = "👥"
EMOJI_CHART   = "📊"

# ── Message formatters ────────────────────────────────────────────────────────

def fmt_success(title: str, body: str = "") -> str:
    msg = f"{EMOJI_OK} <b>{title}</b>"
    if body:
        msg += f"\n{body}"
    return msg

def fmt_error(title: str, body: str = "") -> str:
    msg = f"{EMOJI_ERROR} <b>{title}</b>"
    if body:
        msg += f"\n<i>{body}</i>"
    return msg

def fmt_info(title: str, body: str = "") -> str:
    msg = f"{EMOJI_INFO} <b>{title}</b>"
    if body:
        msg += f"\n{body}"
    return msg

def fmt_warn(title: str, body: str = "") -> str:
    msg = f"{EMOJI_WARN} <b>{title}</b>"
    if body:
        msg += f"\n<i>{body}</i>"
    return msg

def fmt_section(title: str, lines: list[str]) -> str:
    """Render a titled bullet section in Telegram HTML."""
    body = "\n".join(f"  • {l}" for l in lines)
    return f"<b>{title}</b>\n{body}"

def fmt_footer(bot_name: str) -> str:
    return f"\n<i>— {bot_name} · {BRAND_NAME}</i>"

def fmt_status_message(
    bot_name: str,
    status: str,
    fields: dict[str, str],
    footer: bool = True
) -> str:
    """
    Generic /status reply for any bot.
    status: 'online' | 'degraded' | 'offline'
    fields: ordered dict of label -> value lines
    """
    icon = {"online": "🟢", "degraded": "🟡", "offline": "🔴"}.get(status, "⚪")
    lines = [f"{EMOJI_BOT} <b>{bot_name}</b>  {icon} {status.upper()}", ""]
    for k, v in fields.items():
        lines.append(f"<b>{k}:</b> {v}")
    if footer:
        lines.append(fmt_footer(bot_name))
    return "\n".join(lines)

"""
TheBooleanJulian Bot Core — Utils
===================================
SGT timezone helpers, date formatters, and general-purpose utilities
shared across all bots.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

# ── Timezone ──────────────────────────────────────────────────────────────────
SGT = timezone(timedelta(hours=8))
UTC = timezone.utc

def now_sgt() -> datetime:
    """Current time in SGT."""
    return datetime.now(SGT)

def now_utc() -> datetime:
    """Current time in UTC."""
    return datetime.now(UTC)

def to_sgt(dt: datetime) -> datetime:
    """Convert any aware datetime to SGT."""
    return dt.astimezone(SGT)

def fmt_datetime(dt: datetime, include_tz: bool = True) -> str:
    """Human-readable datetime string in SGT."""
    dt = to_sgt(dt)
    base = dt.strftime("%d %b %Y, %H:%M:%S")
    return f"{base} SGT" if include_tz else base

def fmt_date(dt: datetime) -> str:
    return to_sgt(dt).strftime("%d %b %Y")

def fmt_time(dt: datetime) -> str:
    return to_sgt(dt).strftime("%H:%M SGT")

# ── Uptime ────────────────────────────────────────────────────────────────────

_start_time: Optional[datetime] = None

def mark_start() -> None:
    """Call once at bot startup to begin uptime tracking."""
    global _start_time
    _start_time = now_utc()

def get_uptime() -> Optional[timedelta]:
    if _start_time is None:
        return None
    return now_utc() - _start_time

def fmt_uptime() -> str:
    delta = get_uptime()
    if delta is None:
        return "unknown"
    total = int(delta.total_seconds())
    d, rem = divmod(total, 86400)
    h, rem = divmod(rem, 3600)
    m, s   = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)

def get_start_time_iso() -> str:
    if _start_time is None:
        return "—"
    return fmt_datetime(_start_time)

# ── Text helpers ──────────────────────────────────────────────────────────────

def truncate(text: str, max_len: int = 200, suffix: str = "…") -> str:
    return text if len(text) <= max_len else text[:max_len - len(suffix)] + suffix

def plural(n: int, singular: str, plural_form: Optional[str] = None) -> str:
    form = plural_form if plural_form else singular + "s"
    return f"{n} {singular if n == 1 else form}"

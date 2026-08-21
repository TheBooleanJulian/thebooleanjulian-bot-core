"""
TheBooleanJulian Bot Core — Logging
======================================
Every real bot in the fleet calls logging.basicConfig() and silences
httpx/httpcore (they log full request URLs, which include the bot token).
This is that boilerplate, plus an optional rotating file handler for bots
that want persisted logs (monitoring-miku's pattern).
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Third-party loggers that leak the bot token into request-URL debug lines,
# or are just noisy at INFO. Silenced by default; pass silence=() to disable.
DEFAULT_SILENCE = ("httpx", "httpcore", "apscheduler.executors", "telegram.ext.Updater")

# In-memory ring buffer, only populated if setup_logging(buffer=True).
# Used by the health status page's "Recent logs" panel, if a bot wants one.
_log_buffer: list[dict] = []
_LOG_BUFFER_MAX = 200


_buffer_time_formatter = logging.Formatter(datefmt=DATE_FORMAT)


class _BufferHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        _log_buffer.append({
            "time":    _buffer_time_formatter.formatTime(record, DATE_FORMAT),
            "level":   record.levelname,
            "name":    record.name,
            "message": record.getMessage(),
        })
        if len(_log_buffer) > _LOG_BUFFER_MAX:
            _log_buffer.pop(0)


def get_log_buffer(n: int = 50) -> list[dict]:
    """Return the last n buffered log entries. Empty unless setup_logging(buffer=True)."""
    return list(reversed(_log_buffer[-n:]))


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    silence: tuple = DEFAULT_SILENCE,
    buffer: bool = False,
) -> logging.Logger:
    """
    Configure the root logger. Call once at the top of main.py before
    anything else touches logging.

    log_file: if given, also writes DEBUG+ logs to a 5MB x 3 rotating file
              (pass e.g. Path(__file__).parent / "logs" / "bot.log").
    buffer:   if True, keeps the last 200 log lines in memory for a status
              page's "Recent logs" panel (see get_log_buffer()).
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if log_file else level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    root.addHandler(stream_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        root.addHandler(file_handler)

    if buffer:
        root.addHandler(_BufferHandler())

    for name in silence:
        logging.getLogger(name).setLevel(logging.WARNING)

    return root

"""
TheBooleanJulian Bot Core — Health & Status Server
====================================================
Drop-in Flask micro-server for every bot.
Serves:
  GET /           → Beautiful status page (HTML)
  GET /healthz    → {"status": "ok"} for Zeabur uptime checks
  GET /logs       → Last N log lines as JSON

Usage in your bot's main.py:

    from julian_bot_core.health import StatusServer

    server = StatusServer(
        bot_name        = "Miku Monday Bot",
        bot_username    = "@itsmikumondaybot",
        bot_description = "Spreading Hatsune Miku joy every Monday!",
        bot_version     = "2.1.0",
        commands        = [
            ("/start",       "Welcome & register"),
            ("/status",      "Bot status"),
            ("/countdown",   "Time until next Miku Monday"),
            ("/unsubscribe", "Remove channel"),
        ],
        get_subscriber_count = lambda: len(subscribers),   # optional callable
        get_extra_metrics    = lambda: {"Next post": next_post_str},  # optional
        accent_color         = "#00d4c8",   # override per-bot if desired
        icon_emoji           = "🎵",
    )
    server.start(port=8080)   # runs in a background thread
"""

import json
import logging
import threading
from typing import Callable, Optional

from flask import Flask, Response, render_template_string
from .middleware import get_log_buffer
from .utils import fmt_uptime, get_start_time_iso, now_sgt, fmt_datetime
from .branding import BRAND_NAME, BRAND_GITHUB

logger = logging.getLogger(__name__)

# ── Jinja2 template is in the same package ────────────────────────────────────
import os as _os
_TEMPLATE_PATH = _os.path.join(_os.path.dirname(__file__), "status_template.html")


class StatusServer:
    def __init__(
        self,
        bot_name: str,
        bot_username: str,
        bot_description: str,
        bot_version: str              = "1.0.0",
        commands: list[tuple]         = None,
        get_subscriber_count: Optional[Callable[[], int]] = None,
        get_extra_metrics: Optional[Callable[[], dict]]   = None,
        accent_color: str             = "#00d4c8",
        icon_emoji: str               = "🤖",
    ):
        self.bot_name             = bot_name
        self.bot_username         = bot_username
        self.bot_description      = bot_description
        self.bot_version          = bot_version
        self.commands             = commands or []
        self.get_subscriber_count = get_subscriber_count
        self.get_extra_metrics    = get_extra_metrics
        self.accent_color         = accent_color
        self.icon_emoji           = icon_emoji
        self._app                 = self._build_app()

    def _build_app(self) -> Flask:
        app = Flask(__name__)
        app.logger.setLevel(logging.ERROR)  # suppress Flask request logs

        @app.route("/healthz")
        def healthz():
            return Response(
                json.dumps({"status": "ok", "bot": self.bot_name}),
                mimetype="application/json"
            )

        @app.route("/logs")
        def logs():
            return Response(
                json.dumps(get_log_buffer(100)),
                mimetype="application/json"
            )

        @app.route("/")
        def index():
            with open(_TEMPLATE_PATH, "r") as f:
                tmpl = f.read()

            sub_count = None
            if self.get_subscriber_count:
                try:
                    sub_count = self.get_subscriber_count()
                except Exception:
                    pass

            extra = {}
            if self.get_extra_metrics:
                try:
                    extra = self.get_extra_metrics()
                except Exception:
                    pass

            return render_template_string(
                tmpl,
                bot_name          = self.bot_name,
                bot_username      = self.bot_username,
                bot_description   = self.bot_description,
                bot_version       = self.bot_version,
                commands          = self.commands,
                subscriber_count  = sub_count,
                extra_metrics     = extra,
                uptime            = fmt_uptime(),
                start_time        = get_start_time_iso(),
                current_time      = fmt_datetime(now_sgt()),
                logs              = get_log_buffer(30),
                accent_color      = self.accent_color,
                icon_emoji        = self.icon_emoji,
                brand_name        = BRAND_NAME,
                brand_github      = BRAND_GITHUB,
            )

        return app

    def start(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Start the status server in a daemon background thread."""
        t = threading.Thread(
            target=lambda: self._app.run(host=host, port=port, debug=False),
            daemon=True,
            name="status-server",
        )
        t.start()
        logger.info(f"Status server running on http://{host}:{port}/")

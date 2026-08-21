"""
TheBooleanJulian Bot Core — Status Server (Flask backend)
=============================================================
For bots that already depend on Flask (or aren't on Zeabur's uvicorn
auto-detect path). Same constructor shape as SimpleStatusServer, so you
can switch backends without touching the rest of main.py. Requires the
`flask` extra: pip install "thebooleanjulian-bot-core[flask]"
"""

import json
import logging
import os
import threading
from typing import Callable, Optional

from flask import Flask, Response

from .render import render_status_html
from ..branding import BRAND_NAME, BRAND_GITHUB
from ..utils import fmt_uptime, get_start_time_iso, now_sgt, fmt_datetime
from ..logging_setup import get_log_buffer

logger = logging.getLogger(__name__)


class FlaskStatusServer:
    def __init__(
        self,
        bot_name: str,
        bot_username: str,
        bot_description: str,
        bot_version: str = "1.0.0",
        commands: list[tuple] = (),
        get_metrics: Optional[Callable[[], dict]] = None,
        get_sections: Optional[Callable[[], list]] = None,
        accent_color: str = "#00d4c8",
        icon_emoji: str = "🤖",
        show_logs: bool = True,
    ):
        self.bot_name = bot_name
        self.bot_username = bot_username
        self.bot_description = bot_description
        self.bot_version = bot_version
        self.commands = list(commands)
        self.get_metrics = get_metrics
        self.get_sections = get_sections
        self.accent_color = accent_color
        self.icon_emoji = icon_emoji
        self.show_logs = show_logs
        self._app = self._build_app()

    def _safe_call(self, fn, default):
        if not fn:
            return default
        try:
            return fn()
        except Exception:
            logger.exception("status page metrics/sections callback failed")
            return default

    def _build_app(self) -> Flask:
        app = Flask(__name__)
        app.logger.setLevel(logging.ERROR)
        logging.getLogger("werkzeug").setLevel(logging.ERROR)

        @app.route("/healthz")
        def healthz():
            return Response(json.dumps({"status": "ok", "bot": self.bot_name}), mimetype="application/json")

        @app.route("/logs")
        def logs():
            return Response(json.dumps(get_log_buffer(100)), mimetype="application/json")

        @app.route("/")
        def index():
            html = render_status_html(
                bot_name=self.bot_name,
                bot_username=self.bot_username,
                bot_description=self.bot_description,
                bot_version=self.bot_version,
                icon_emoji=self.icon_emoji,
                accent_color=self.accent_color,
                uptime=fmt_uptime(),
                start_time=get_start_time_iso(),
                current_time=fmt_datetime(now_sgt()),
                brand_name=BRAND_NAME,
                brand_github=BRAND_GITHUB,
                commands=self.commands,
                metrics=self._safe_call(self.get_metrics, {}),
                sections=self._safe_call(self.get_sections, []),
                logs=get_log_buffer(30) if self.show_logs else (),
            )
            return Response(html, mimetype="text/html")

        return app

    def start(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Start in a daemon background thread. port defaults to $PORT or 8080."""
        port = port or int(os.environ.get("PORT", 8080))
        t = threading.Thread(
            target=lambda: self._app.run(host=host, port=port, debug=False),
            daemon=True,
            name="status-server",
        )
        t.start()
        logger.info(f"Status server running on http://{host}:{port}/")

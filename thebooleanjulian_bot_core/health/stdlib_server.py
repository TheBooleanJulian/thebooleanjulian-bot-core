"""
TheBooleanJulian Bot Core — Status Server (stdlib backend)
==============================================================
Zero extra dependencies. This is the backend openclaw and clawsune use
deliberately: Zeabur's uvicorn auto-detection misfires against a Flask
app, so a plain http.server sidesteps it entirely. Default backend for
new bots deployed on Zeabur unless you already depend on Flask elsewhere.
"""

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Optional

from .render import render_status_html
from ..branding import BRAND_NAME, BRAND_GITHUB
from ..utils import fmt_uptime, get_start_time_iso, now_sgt, fmt_datetime
from ..logging_setup import get_log_buffer

logger = logging.getLogger(__name__)


class SimpleStatusServer:
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

    def _safe_call(self, fn, default):
        if not fn:
            return default
        try:
            return fn()
        except Exception:
            logger.exception("status page metrics/sections callback failed")
            return default

    def _render_index(self) -> bytes:
        return render_status_html(
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
        ).encode("utf-8")

    def _make_handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path in ("/", "/status"):
                    body = server._render_index()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/healthz":
                    body = json.dumps({"status": "ok", "bot": server.bot_name}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/logs":
                    body = json.dumps(get_log_buffer(100)).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):  # noqa: A002
                pass  # suppress per-request access logs

        return Handler

    def start(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Start in a daemon background thread. port defaults to $PORT or 8080."""
        port = port or int(os.environ.get("PORT", 8080))
        server = HTTPServer((host, port), self._make_handler())
        t = threading.Thread(target=server.serve_forever, daemon=True, name="status-server")
        t.start()
        logger.info(f"Status server running on http://{host}:{port}/")

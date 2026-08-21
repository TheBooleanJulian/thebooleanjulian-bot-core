"""
Two interchangeable backends, same constructor shape:

  SimpleStatusServer — stdlib http.server, zero extra deps. Default: the
                        Zeabur-safe choice (see stdlib_server.py docstring).
  FlaskStatusServer   — Flask-based, for bots already depending on Flask.
                        Requires the `flask` extra.

`StatusServer` aliases SimpleStatusServer for drop-in convenience.
"""

from .stdlib_server import SimpleStatusServer
from .stdlib_server import SimpleStatusServer as StatusServer

__all__ = ["SimpleStatusServer", "StatusServer", "FlaskStatusServer"]


def __getattr__(name):
    # Lazy import so bots that don't have flask installed never pay for it
    # (or crash at import time just from `from ...health import StatusServer`).
    if name == "FlaskStatusServer":
        from .flask_server import FlaskStatusServer
        return FlaskStatusServer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

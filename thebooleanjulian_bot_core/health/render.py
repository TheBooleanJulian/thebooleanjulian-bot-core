"""
TheBooleanJulian Bot Core — Status Page Renderer
====================================================
Single source of truth for the branded status-page HTML, shared by both
health-server backends (stdlib and Flask) so the look stays identical no
matter which transport a given bot's deploy target needs. Plain string
building, no Jinja2 — the stdlib backend has no template-engine dependency.
"""

import html as _html

_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --accent: __ACCENT__; --bg: #060910; --bg-card: #0c1220;
  --border: __ACCENT__18; --text: #dde6f0; --text-muted: #6b7280;
  --online: #00e5b0; --font: -apple-system, 'Segoe UI', Roboto, sans-serif;
  --mono: 'JetBrains Mono', ui-monospace, monospace;
}
body {
  background: var(--bg); color: var(--text); font-family: var(--font);
  min-height: 100vh; padding: 48px 24px 64px;
}
.page { max-width: 760px; margin: 0 auto; }
.header { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 36px; }
.header-icon { font-size: 2.6rem; }
.header-title { font-size: 1.8rem; font-weight: 700; color: #fff; }
.header-title span { color: var(--accent); }
.header-sub { color: var(--text-muted); margin-top: 4px; font-size: 0.9rem; }
.header-handle {
  display: inline-block; margin-top: 8px; font-family: var(--mono); font-size: 0.75rem;
  color: var(--accent); border: 1px solid var(--accent); padding: 2px 10px;
  border-radius: 20px; text-decoration: none;
}
.status-badge {
  margin-left: auto; display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--online); border: 1px solid var(--online); padding: 5px 12px;
  border-radius: 20px; white-space: nowrap;
}
.dot { width: 6px; height: 6px; background: var(--online); border-radius: 50%; }
.section { margin-bottom: 28px; }
.section-label {
  font-size: 0.68rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 10px;
}
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 18px 22px; }
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
.metric { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; text-align: center; }
.metric-value { font-size: 1.4rem; font-weight: 700; color: var(--accent); display: block; }
.metric-label { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; display: block; }
.cmd-row { display: flex; gap: 12px; padding: 8px 4px; border-bottom: 1px solid var(--border); }
.cmd-row:last-child { border-bottom: none; }
.cmd-name { font-family: var(--mono); font-size: 0.8rem; color: var(--accent); min-width: 120px; }
.cmd-desc { font-size: 0.85rem; color: var(--text-muted); }
.log-row { display: flex; gap: 10px; padding: 4px 2px; font-family: var(--mono); font-size: 0.72rem; }
.log-time { color: var(--text-muted); flex-shrink: 0; }
.log-level { font-weight: 700; flex-shrink: 0; width: 56px; }
.log-level.WARNING { color: #f6c90e; }
.log-level.ERROR, .log-level.CRITICAL { color: #ff4d6d; }
.log-level.INFO { color: var(--accent); }
.log-msg { color: var(--text-muted); word-break: break-word; }
.log-empty { color: var(--text-muted); font-size: 0.8rem; text-align: center; padding: 12px; }
.footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 0.72rem; color: var(--text-muted); }
.footer a { color: var(--accent); text-decoration: none; }
"""

_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta http-equiv="refresh" content="30"/>
<title>{bot_name} — Status</title>
<style>{css}</style>
</head>
<body>
<div class="page">
  <header class="header">
    <div class="header-icon">{icon_emoji}</div>
    <div>
      <div class="header-title">{bot_name}</div>
      <div class="header-sub">{bot_description}</div>
      <a class="header-handle" href="https://t.me/{bot_username_bare}" target="_blank">{bot_username}</a>
    </div>
    <span class="status-badge"><span class="dot"></span>Online</span>
  </header>

  <div class="section">
    <div class="section-label">System</div>
    <div class="metrics">
      <div class="metric"><span class="metric-value">{uptime}</span><span class="metric-label">Uptime</span></div>
      <div class="metric"><span class="metric-value">{bot_version}</span><span class="metric-label">Version</span></div>
      {metric_cards}
    </div>
  </div>

  {command_section}

  {extra_sections}

  <div class="section">
    <div class="section-label">Recent logs</div>
    <div class="card">{log_rows}</div>
  </div>

  <footer class="footer">
    Started {start_time} · Now {current_time}<br/>
    Built by <a href="{brand_github}" target="_blank">{brand_name}</a>
  </footer>
</div>
</body>
</html>"""


def render_status_html(
    bot_name: str,
    bot_username: str,
    bot_description: str,
    bot_version: str,
    icon_emoji: str,
    accent_color: str,
    uptime: str,
    start_time: str,
    current_time: str,
    brand_name: str,
    brand_github: str,
    commands: list[tuple] = (),
    metrics: dict = None,
    sections: list[dict] = (),
    logs: list[dict] = (),
) -> str:
    """
    metrics: ordered dict of label -> value, rendered as extra metric cards
             (replaces the old separate subscriber_count/extra_metrics args
             — a bot that wants a featured subscriber count just puts it
             first in the dict).
    sections: [{"title": str, "html": str}, ...] — free-form extra cards,
              e.g. a "Next scheduled run" block (mikew-gcal-v3's pattern).
    logs: [{"time": str, "level": str, "message": str}, ...]
    """
    metrics = metrics or {}
    metric_cards = "".join(
        f'<div class="metric"><span class="metric-value" style="font-size:1.05rem">'
        f'{_html.escape(str(v))}</span><span class="metric-label">{_html.escape(k)}</span></div>'
        for k, v in metrics.items()
    )

    if commands:
        rows = "".join(
            f'<div class="cmd-row"><span class="cmd-name">{_html.escape(c)}</span>'
            f'<span class="cmd-desc">{_html.escape(d)}</span></div>'
            for c, d in commands
        )
        command_section = (
            f'<div class="section"><div class="section-label">Commands</div>'
            f'<div class="card">{rows}</div></div>'
        )
    else:
        command_section = ""

    extra_sections = "".join(
        f'<div class="section"><div class="section-label">{_html.escape(s["title"])}</div>'
        f'<div class="card">{s["html"]}</div></div>'
        for s in sections
    )

    if logs:
        log_rows = "".join(
            f'<div class="log-row"><span class="log-time">{_html.escape(l["time"])}</span>'
            f'<span class="log-level {l["level"]}">{_html.escape(l["level"])}</span>'
            f'<span class="log-msg">{_html.escape(l["message"])}</span></div>'
            for l in logs
        )
    else:
        log_rows = '<div class="log-empty">no log entries yet</div>'

    return _SHELL.format(
        bot_name=_html.escape(bot_name),
        bot_description=_html.escape(bot_description),
        bot_username=_html.escape(bot_username),
        bot_username_bare=_html.escape(bot_username.lstrip("@")),
        bot_version=_html.escape(bot_version),
        icon_emoji=icon_emoji,
        uptime=_html.escape(uptime),
        start_time=_html.escape(start_time),
        current_time=_html.escape(current_time),
        brand_name=_html.escape(brand_name),
        brand_github=brand_github,
        metric_cards=metric_cards,
        command_section=command_section,
        extra_sections=extra_sections,
        log_rows=log_rows,
        css=_CSS.replace("__ACCENT__", accent_color),
    )

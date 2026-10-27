// Health check JSON and the branded status page. JS counterpart of health/render.py, restyled on the
// Julian Unified UI tokens (brand-tokens.js), so a brand change in tbj-brand reaches every bot's page.
//
//   if (url.pathname === '/healthz') return healthz(env, { checks });
//   if (url.pathname === '/')        return statusPage(env, { name, username, description, commands, metrics });
//   const brand = serveBrand(request); if (brand) return brand;   // /brand/tokens.css for a bot's own pages
import { BRAND_CSS } from './brand-tokens.js';
import { BRAND_NAME, BRAND_GITHUB, escapeHtml as esc } from './branding.js';
import { fmtDatetime, fmtSince } from './time.js';
import { BOT_CORE_VERSION } from './version.js';

// What the fan-out gate reads: the bot-core commit this Worker was built with (set at deploy time by
// propagate_workers.py as the BOT_CORE_SHA var) plus whatever self-checks the bot runs.
export function botCoreInfo(env) {
  return { version: BOT_CORE_VERSION, sha: env.BOT_CORE_SHA || 'local' };
}

export function healthz(env, { checks = {}, extra = {} } = {}) {
  const ok = Object.values(checks).every((v) => v === 'ok');
  const body = {
    bot: env.BOT_NAME || 'bot',
    status: ok ? 'pass' : 'fail',
    checks,
    bot_core: botCoreInfo(env),
    deployed_at: env.CF_VERSION_METADATA?.timestamp || null,
    ...extra
  };
  return new Response(JSON.stringify(body, null, 2), {
    status: ok ? 200 : 500,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
  });
}

export function serveBrand(request) {
  if (new URL(request.url).pathname !== '/brand/tokens.css') return null;
  return new Response(BRAND_CSS, { headers: { 'Content-Type': 'text/css; charset=utf-8', 'Cache-Control': 'public, max-age=3600' } });
}

const CSS = `
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-sans); font-size: 14px; min-height: 100vh; padding: var(--space-7) var(--space-4) var(--space-7); }
.page { max-width: 760px; margin: 0 auto; }
.hairline { height: 1px; background: linear-gradient(90deg, var(--cyan), var(--magenta)); margin-bottom: var(--space-6); opacity: .8; }
.header { display: flex; align-items: flex-start; gap: var(--space-4); margin-bottom: var(--space-6); }
.header-icon { font-size: 2.4rem; line-height: 1; }
.header-title { font-family: var(--font-display); font-size: 1.6rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
.header-sub { color: var(--ink-muted); margin-top: var(--space-1); }
.header-handle { display: inline-block; margin-top: var(--space-2); font-family: var(--font-mono); font-size: .75rem; color: var(--cyan-ink); border: 1px solid var(--line-strong); padding: 2px var(--space-3); border-radius: var(--radius-pill); text-decoration: none; }
.header-handle:hover { border-color: var(--cyan-ink); background: var(--cyan-tint); }
.badge { margin-left: auto; display: inline-flex; align-items: center; gap: var(--space-2); font-family: var(--font-display); font-size: .7rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--success); border: 1px solid var(--success); padding: var(--space-1) var(--space-3); border-radius: var(--radius-pill); white-space: nowrap; }
.badge.fail { color: var(--danger); border-color: var(--danger); }
.dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.section { margin-bottom: var(--space-5); }
.label { font-family: var(--font-display); font-size: .7rem; font-weight: 600; letter-spacing: .15em; text-transform: uppercase; color: var(--ink-muted); margin-bottom: var(--space-2); }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-md); padding: var(--space-4); }
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--space-3); }
.metric { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-md); padding: var(--space-4); text-align: center; }
.metric-value { display: block; font-family: var(--font-mono); font-size: 1.15rem; font-weight: 600; color: var(--cyan-ink); word-break: break-word; }
.metric-label { display: block; margin-top: var(--space-1); font-size: .7rem; color: var(--ink-muted); text-transform: uppercase; letter-spacing: .06em; }
.row { display: flex; gap: var(--space-3); padding: var(--space-2) var(--space-1); border-bottom: 1px solid var(--line); }
.row:last-child { border-bottom: none; }
.cmd { font-family: var(--font-mono); font-size: .8rem; color: var(--cyan-ink); min-width: 130px; }
.desc { color: var(--ink-muted); }
.footer { text-align: center; margin-top: var(--space-6); padding-top: var(--space-4); border-top: 1px solid var(--line); font-size: .75rem; color: var(--ink-muted); }
.footer a { color: var(--cyan-ink); text-decoration: none; }
.mono { font-family: var(--font-mono); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
`;

export function renderStatusPage({ name, username = '', description = '', icon = '🤖', ok = true, version = '', deployedAt = null,
  commands = [], metrics = {}, sections = [], now = new Date() }) {
  const bare = username.replace(/^@/, '');
  const metricCards = Object.entries(metrics)
    .map(([k, v]) => `<div class="metric"><span class="metric-value">${esc(v)}</span><span class="metric-label">${esc(k)}</span></div>`).join('');
  const cmdRows = commands.map(([c, d]) => `<div class="row"><span class="cmd">${esc(c)}</span><span class="desc">${esc(d)}</span></div>`).join('');
  const extra = sections.map((s) => `<div class="section"><div class="label">${esc(s.title)}</div><div class="panel">${s.html}</div></div>`).join('');
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta http-equiv="refresh" content="60"/>
<title>${esc(name)} — Status</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=IBM+Plex+Sans:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet"/>
<style>${BRAND_CSS}${CSS}</style>
</head>
<body>
<div class="page">
  <div class="hairline"></div>
  <header class="header">
    <div class="header-icon">${icon}</div>
    <div>
      <div class="header-title">${esc(name)}</div>
      <div class="header-sub">${esc(description)}</div>
      ${bare ? `<a class="header-handle" href="https://t.me/${esc(bare)}" target="_blank" rel="noopener">@${esc(bare)}</a>` : ''}
    </div>
    <span class="badge${ok ? '' : ' fail'}"><span class="dot"></span>${ok ? 'Online' : 'Degraded'}</span>
  </header>
  <div class="section">
    <div class="label">System</div>
    <div class="metrics">
      <div class="metric"><span class="metric-value">${esc(fmtSince(deployedAt, now))}</span><span class="metric-label">Since deploy</span></div>
      ${version ? `<div class="metric"><span class="metric-value">${esc(version)}</span><span class="metric-label">Version</span></div>` : ''}
      ${metricCards}
    </div>
  </div>
  ${cmdRows ? `<div class="section"><div class="label">Commands</div><div class="panel">${cmdRows}</div></div>` : ''}
  ${extra}
  <footer class="footer">
    Deployed ${esc(deployedAt ? fmtDatetime(new Date(deployedAt)) : 'unknown')} · Now <span class="mono">${esc(fmtDatetime(now))}</span><br/>
    Built by <a href="${BRAND_GITHUB}" target="_blank" rel="noopener">${BRAND_NAME}</a>
  </footer>
</div>
</body>
</html>`;
}

export function statusPage(env, opts) {
  const html = renderStatusPage({ deployedAt: env.CF_VERSION_METADATA?.timestamp, version: botCoreInfo(env).sha.slice(0, 7), ...opts });
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
}

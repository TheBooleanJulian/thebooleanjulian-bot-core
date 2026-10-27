// Singapore-time and text helpers. JS counterpart of utils.py (no process uptime on Workers:
// use the deployment timestamp from the version_metadata binding instead).

export const TZ = 'Asia/Singapore';

const parts = (date, opts) => new Intl.DateTimeFormat('en-GB', { timeZone: TZ, ...opts }).format(date);

export const fmtDate = (date = new Date()) => parts(date, { day: 'numeric', month: 'short', year: 'numeric' });
export const fmtTime = (date = new Date()) => parts(date, { hour: '2-digit', minute: '2-digit', hour12: false });
export const fmtDatetime = (date = new Date(), includeTz = true) => `${fmtDate(date)}, ${fmtTime(date)}${includeTz ? ' SGT' : ''}`;

// "3d 4h", "5h 12m", "42s" since an ISO timestamp (e.g. env.CF_VERSION_METADATA.timestamp).
export function fmtSince(iso, now = new Date()) {
  if (!iso) return 'unknown';
  let s = Math.max(0, Math.floor((now - new Date(iso)) / 1000));
  const d = Math.floor(s / 86400); s -= d * 86400;
  const h = Math.floor(s / 3600); s -= h * 3600;
  const m = Math.floor(s / 60); s -= m * 60;
  if (d) return `${d}d ${h}h`;
  if (h) return `${h}h ${m}m`;
  if (m) return `${m}m ${s}s`;
  return `${s}s`;
}

export const truncate = (text, maxLen = 200, suffix = '…') => (text.length <= maxLen ? text : text.slice(0, maxLen - suffix.length) + suffix);
export const plural = (n, singular, pluralForm) => `${n} ${n === 1 ? singular : pluralForm || singular + 's'}`;

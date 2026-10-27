// Brand constants and Telegram HTML formatters. JS counterpart of branding.py.
// Colours are not hard-coded here: pages use the Julian Unified UI tokens (brand-tokens.js).

export const BRAND_NAME = 'TheBooleanJulian';
export const BRAND_HANDLE = '@TheBooleanJulian';
export const BRAND_GITHUB = 'https://github.com/TheBooleanJulian';
export const BRAND_SITE = 'https://thebooleanjulian.dev';
export const BRAND_FOOTER = `Built by ${BRAND_NAME} · ${BRAND_GITHUB}`;

export const EMOJI = {
  ok: '✅', error: '❌', warn: '⚠️', info: '💡', loading: '⏳',
  bot: '🤖', clock: '🕐', users: '👥', chart: '📊',
  mikuSparkle: '✦', mikuNote: '♪', mikuTeal: '🩵', mikuStar: '🌟'
};

// Telegram HTML needs <, > and & escaped in user-supplied text.
export const escapeHtml = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const block = (emoji, title, body, italic) =>
  `${emoji} <b>${title}</b>` + (body ? `\n${italic ? `<i>${body}</i>` : body}` : '');

export const fmtSuccess = (title, body = '') => block(EMOJI.ok, title, body, false);
export const fmtError = (title, body = '') => block(EMOJI.error, title, body, true);
export const fmtInfo = (title, body = '') => block(EMOJI.info, title, body, false);
export const fmtWarn = (title, body = '') => block(EMOJI.warn, title, body, true);
export const fmtSection = (title, lines) => `<b>${title}</b>\n${lines.map((l) => `  • ${l}`).join('\n')}`;
export const fmtFooter = (botName) => `\n<i>— ${botName} · ${BRAND_NAME}</i>`;

// Generic /status reply. status: 'online' | 'degraded' | 'offline'
export function fmtStatusMessage(botName, status, fields, footer = true) {
  const icon = { online: '🟢', degraded: '🟡', offline: '🔴' }[status] || '⚪';
  const lines = [`${EMOJI.bot} <b>${botName}</b>  ${icon} ${String(status).toUpperCase()}`, ''];
  for (const [k, v] of Object.entries(fields)) lines.push(`<b>${k}:</b> ${v}`);
  if (footer) lines.push(fmtFooter(botName));
  return lines.join('\n');
}

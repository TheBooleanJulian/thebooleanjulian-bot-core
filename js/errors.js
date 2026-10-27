// Error boundary for handlers. JS counterpart of error_handling.py: the user gets a friendly reply,
// the owner gets the (token-redacted) error, and the webhook still answers 200 so Telegram
// doesn't retry the same update forever.
import { log, redact } from './log.js';
import { api } from './telegram.js';
import { adminIds } from './admin.js';
import { escapeHtml } from './branding.js';

export const DEFAULT_FRIENDLY_MESSAGE = '⚠️ Something went wrong on my side. Julian has been notified.';

export function errorBoundary(handler, { friendly = DEFAULT_FRIENDLY_MESSAGE, notifyOwner = true } = {}) {
  return async (ctx) => {
    try {
      return await handler(ctx);
    } catch (err) {
      const where = ctx.message?.text?.split(/\s/)[0] || ctx.data || 'handler';
      log.error('handler failed', { where, error: err.message });
      const chatId = ctx.message?.chat?.id ?? ctx.query?.message?.chat?.id;
      if (chatId != null && friendly) {
        await api(ctx.env, 'sendMessage', { chat_id: chatId, text: friendly }).catch(() => {});
      }
      const owner = adminIds(ctx.env)[0];
      if (notifyOwner && owner && String(owner) !== String(chatId)) {
        const text = `❌ <b>${escapeHtml(ctx.env.BOT_NAME || 'bot')}</b> error in <code>${escapeHtml(where)}</code>\n<pre>${escapeHtml(redact(err.stack || err.message)).slice(0, 3500)}</pre>`;
        await api(ctx.env, 'sendMessage', { chat_id: owner, text, parse_mode: 'HTML' }).catch(() => {});
      }
    }
  };
}

// Inline keyboard builders (Bot API reply_markup objects). JS counterpart of ui.py.
import { api } from './telegram.js';

const markup = (rows) => ({ inline_keyboard: rows });

export const confirmKeyboard = ({ confirmData = 'confirm', cancelData = 'cancel', confirmLabel = '✅ Confirm', cancelLabel = '❌ Cancel' } = {}) =>
  markup([[{ text: confirmLabel, callback_data: confirmData }, { text: cancelLabel, callback_data: cancelData }]]);

export const backKeyboard = ({ backData = 'back', backLabel = '← Back' } = {}) =>
  markup([[{ text: backLabel, callback_data: backData }]]);

export const urlButtonKeyboard = (label, url) => markup([[{ text: label, url }]]);

// items: [[label, callback_data], ...]; prev/next buttons carry `${navPrefix}:${page}`.
export function paginatedKeyboard(items, { page = 0, pageSize = 5, navPrefix = 'page' } = {}) {
  const start = page * pageSize;
  const rows = items.slice(start, start + pageSize).map(([text, data]) => [{ text, callback_data: data }]);
  const nav = [];
  if (page > 0) nav.push({ text: '◀ Prev', callback_data: `${navPrefix}:${page - 1}` });
  if (start + pageSize < items.length) nav.push({ text: 'Next ▶', callback_data: `${navPrefix}:${page + 1}` });
  if (nav.length) rows.push(nav);
  return markup(rows);
}

export const LOADING_MSG = '⏳ <i>Processing…</i>';
export const DONE_MSG = '✅ Done.';

// Send a loading placeholder; returns the sent message so it can be edited into the result.
export const sendLoading = (env, chatId) => api(env, 'sendMessage', { chat_id: chatId, text: LOADING_MSG, parse_mode: 'HTML' });

export const editToResult = (env, message, text) =>
  api(env, 'editMessageText', { chat_id: message.chat.id, message_id: message.message_id, text, parse_mode: 'HTML' });

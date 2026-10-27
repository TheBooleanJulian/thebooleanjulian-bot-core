// node --test   (Node 22+, no dependencies)
import { test, afterEach } from 'node:test';
import assert from 'node:assert/strict';

import { fmtSuccess, fmtError, fmtStatusMessage, fmtSection, escapeHtml } from '../js/branding.js';
import { confirmKeyboard, paginatedKeyboard, urlButtonKeyboard } from '../js/ui.js';
import { fmtSince, fmtDatetime, plural, truncate } from '../js/time.js';
import { rateLimit, _resetRateLimits } from '../js/ratelimit.js';
import { errorBoundary } from '../js/errors.js';
import { healthz, renderStatusPage, serveBrand } from '../js/health.js';
import * as core from '../js/index.js';

afterEach(() => _resetRateLimits());

test('branding formatters match the Python edition', () => {
  assert.equal(fmtSuccess('Saved'), '✅ <b>Saved</b>');
  assert.equal(fmtError('Failed', 'why'), '❌ <b>Failed</b>\n<i>why</i>');
  assert.equal(fmtSection('List', ['a', 'b']), '<b>List</b>\n  • a\n  • b');
  assert.match(fmtStatusMessage('Bot', 'online', { Users: 3 }), /🤖 <b>Bot<\/b>  🟢 ONLINE\n\n<b>Users:<\/b> 3\n\n<i>— Bot · TheBooleanJulian<\/i>/);
  assert.equal(escapeHtml('<a & b>'), '&lt;a &amp; b&gt;');
});

test('keyboards build Bot API reply_markup', () => {
  assert.deepEqual(confirmKeyboard().inline_keyboard[0].map((b) => b.callback_data), ['confirm', 'cancel']);
  assert.deepEqual(urlButtonKeyboard('Open', 'https://x').inline_keyboard, [[{ text: 'Open', url: 'https://x' }]]);
  const items = Array.from({ length: 7 }, (_, i) => [`item ${i}`, `pick:${i}`]);
  const p0 = paginatedKeyboard(items, { page: 0, pageSize: 5 }).inline_keyboard;
  assert.equal(p0.length, 6);
  assert.deepEqual(p0[5], [{ text: 'Next ▶', callback_data: 'page:1' }]);
  const p1 = paginatedKeyboard(items, { page: 1, pageSize: 5 }).inline_keyboard;
  assert.deepEqual(p1.at(-1), [{ text: '◀ Prev', callback_data: 'page:0' }]);
});

test('time helpers use Singapore time', () => {
  assert.equal(fmtDatetime(new Date('2026-10-27T02:30:00Z')), '27 Oct 2026, 10:30 SGT');
  assert.equal(fmtSince('2026-10-27T00:00:00Z', new Date('2026-10-28T03:00:00Z')), '1d 3h');
  assert.equal(fmtSince(null), 'unknown');
  assert.equal(plural(1, 'chat'), '1 chat');
  assert.equal(plural(2, 'chat'), '2 chats');
  assert.equal(truncate('abcdef', 4), 'abc…');
});

test('rateLimit lets max calls through per user, then blocks', async () => {
  let n = 0;
  const limited = rateLimit(() => { n++; }, { calls: 2, period: 60, key: 't' });
  for (let i = 0; i < 4; i++) await limited({ from: { id: 1 } });
  await limited({ from: { id: 2 } });
  assert.equal(n, 3);
});

test('errorBoundary swallows the error and replies with the friendly message', async () => {
  const sent = [];
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => { sent.push(JSON.parse(init.body)); return new Response('{"ok":true,"result":{}}'); };
  try {
    const wrapped = errorBoundary(() => { throw new Error('boom'); });
    await wrapped({ env: { BOT_TOKEN: '1:x', OWNER_TELEGRAM_ID: '99' }, message: { text: '/go', chat: { id: 5 } } });
  } finally {
    globalThis.fetch = realFetch;
  }
  assert.equal(sent[0].chat_id, 5);
  assert.equal(sent[1].chat_id, '99');
  assert.match(sent[1].text, /boom/);
});

test('healthz reports bot-core sha and fails when a check fails', async () => {
  const ok = await healthz({ BOT_NAME: 'x', BOT_CORE_SHA: 'abc123' }, { checks: { a: 'ok' } });
  assert.equal(ok.status, 200);
  assert.equal((await ok.json()).bot_core.sha, 'abc123');
  const bad = await healthz({}, { checks: { a: 'FAIL: no' } });
  assert.equal(bad.status, 500);
});

test('status page is branded with Unified UI tokens and escapes input', () => {
  const html = renderStatusPage({ name: '<Bot>', username: '@x_bot', commands: [['/start', 'hi']], metrics: { Chats: 3 }, deployedAt: '2026-10-27T00:00:00Z' });
  assert.match(html, /--cyan: #00e5ff/i);
  assert.match(html, /Chakra Petch/);
  assert.match(html, /&lt;Bot&gt;/);
  assert.match(html, /t\.me\/x_bot/);
});

test('serveBrand only answers /brand/tokens.css', async () => {
  assert.equal(serveBrand(new Request('https://x/other')), null);
  const r = serveBrand(new Request('https://x/brand/tokens.css'));
  assert.match(await r.text(), /--magenta/);
});

test('index re-exports every module', () => {
  for (const name of ['api', 'createRouter', 'isAdmin', 'errorBoundary', 'rateLimit', 'fmtSuccess', 'confirmKeyboard', 'fmtDatetime', 'healthz', 'BRAND_CSS', 'BOT_CORE_VERSION']) {
    assert.ok(name in core, name);
  }
});

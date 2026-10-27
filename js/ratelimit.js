// Per-user sliding-window rate limit. JS counterpart of ratelimit.py.
// Best effort: state lives in the Worker isolate's memory, so limits reset when the isolate is
// recycled and aren't shared across Cloudflare locations. Good enough to stop a user hammering an
// expensive command; use a Durable Object if a bot ever needs a hard limit.

const calls = new Map(); // `${key}:${userId}` -> [timestamps]

export function rateLimit(handler, { calls: max = 3, period = 10, key = handler.name || 'cmd', message = '⏳ Slow down a little, try again in a few seconds.', reply } = {}) {
  return async (ctx) => {
    const user = ctx.from?.id;
    if (user == null) return handler(ctx);
    const id = `${key}:${user}`;
    const now = Date.now();
    const recent = (calls.get(id) || []).filter((t) => now - t < period * 1000);
    if (recent.length >= max) {
      calls.set(id, recent);
      if (reply) await reply(ctx, message);
      return undefined;
    }
    recent.push(now);
    calls.set(id, recent);
    return handler(ctx);
  };
}

export const _resetRateLimits = () => calls.clear(); // tests

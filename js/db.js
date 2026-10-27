// Postgres for Workers, through the app's own Cloudflare Hyperdrive config onto the shared
// "thebooleanjulian" Supabase project (one schema + one role per app, see thebooleanjulian-db).
//
// Import it on its own — 'thebooleanjulian-bot-core/db' — it is the one module with a dependency
// (the `postgres` driver) and it needs `"compatibility_flags": ["nodejs_compat"]` in wrangler.jsonc.
//
//   "hyperdrive": [{ "binding": "HYPERDRIVE", "id": "<from thebooleanjulian-db/scripts/provision.mjs>" }]
//
//   const n = await withDb(env, ctx, (sql) => sql`select count(*)::int as n from my_app.things`);
import postgres from 'postgres';

// One client per request, as Hyperdrive recommends: Hyperdrive does the pooling, the Worker must not.
// Tests can pass a fake tagged-template function as env.SQL.
export function connect(env, binding = 'HYPERDRIVE') {
  if (env.SQL) return env.SQL;
  const hd = env[binding];
  if (!hd?.connectionString) throw new Error(`Hyperdrive binding ${binding} is missing from wrangler.jsonc`);
  return postgres(hd.connectionString, { max: 5, fetch_types: false });
}

// Runs fn(sql) and closes the client afterwards (in the background when a ctx is given).
export async function withDb(env, ctx, fn, binding = 'HYPERDRIVE') {
  const sql = connect(env, binding);
  try {
    return await fn(sql);
  } finally {
    if (!env.SQL) {
      const closing = sql.end({ timeout: 5 });
      if (ctx?.waitUntil) ctx.waitUntil(closing);
      else await closing;
    }
  }
}

// For /healthz: 'ok' or 'FAIL: <reason>' (never the connection string).
export async function dbCheck(env, ctx, binding = 'HYPERDRIVE') {
  try {
    await withDb(env, ctx, (sql) => sql`select 1`, binding);
    return 'ok';
  } catch (err) {
    return `FAIL: ${String(err.message).replace(/postgres(ql)?:\/\/\S+/g, '<conn>')}`;
  }
}

// node --test   db.js without a database: binding checks, fake injection, and no credential leaks.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { connect, withDb, dbCheck } from '../js/db.js';

test('connect refuses when the Hyperdrive binding is missing', () => {
  assert.throws(() => connect({}), /Hyperdrive binding HYPERDRIVE is missing/);
});

test('withDb uses an injected fake client and returns its result', async () => {
  const fake = (strings, ...values) => Promise.resolve([{ q: strings.join('?'), values }]);
  const rows = await withDb({ SQL: fake }, null, (sql) => sql`select ${1}`);
  assert.deepEqual(rows, [{ q: 'select ?', values: [1] }]);
});

test('dbCheck reports ok, and failures never include a connection string', async () => {
  assert.equal(await dbCheck({ SQL: () => Promise.resolve([]) }), 'ok');
  const failing = () => Promise.reject(new Error('connect failed for postgres://u:secret@host:5432/db'));
  const verdict = await dbCheck({ SQL: failing });
  assert.match(verdict, /^FAIL: /);
  assert.doesNotMatch(verdict, /secret/);
});

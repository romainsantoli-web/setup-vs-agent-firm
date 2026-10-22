import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createLocalLeaderboard } from '../src/services/leaderboard.js';
import { defaultSave } from '../src/core/storage.js';

test('classement local : garde le meilleur temps et l’historique récent', () => {
  const save = defaultSave(); let writes = 0;
  const lb = createLocalLeaderboard(() => save, () => { writes++; });
  assert.deepEqual(lb.submit(20261021, 61.27), { record: true, best: 61.3 });
  assert.equal(lb.submit(20261021, 70).record, false);
  assert.equal(lb.submit(20261021, 42).record, true);
  lb.submit(20261022, 50);
  assert.equal(lb.best(20261021), 42);
  assert.equal(lb.best(20261020), null);
  assert.deepEqual(lb.history(1), [{ day: 20261022, seconds: 50 }]);
  assert.equal(writes, 3);
});

test('classement local : résultats invalides refusés', () => {
  const lb = createLocalLeaderboard(() => defaultSave(), () => {});
  assert.throws(() => lb.submit(20261022, 0), RangeError);
  assert.throws(() => lb.submit(20261022, -5), RangeError);
  assert.throws(() => lb.submit('20261022', 40), RangeError);
  assert.throws(() => lb.submit(20261022, 999999), RangeError);
});

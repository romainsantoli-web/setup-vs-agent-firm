import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sanitize, defaultSave, loadSave, writeSave, memoryStorage, SAVE_KEY } from '../src/core/storage.js';
import { createAnalytics } from '../src/core/analytics.js';

test('sauvegarde : une sauvegarde valide est conservée', () => {
  const raw = { ...defaultSave(), level: 14, hints: 5, owned: ['pastel', 'neon'], theme: 'neon', stars: { 1: 3, 2: 2 }, daily: { 20261022: 48.2 } };
  const s = sanitize(raw);
  assert.equal(s.level, 14);
  assert.equal(s.theme, 'neon');
  assert.deepEqual(s.stars, { 1: 3, 2: 2 });
  assert.equal(s.daily[20261022], 48.2);
});
test('sauvegarde : une sauvegarde corrompue retombe sur des valeurs sûres', () => {
  const s = sanitize({ level: -4, hints: 'beaucoup', owned: ['../hack', 'neon', 42], theme: 'luxe', stars: { 1: 99, x: 3 }, daily: { bad: 5, 20261022: -1 }, noAds: 'oui' });
  assert.equal(s.level, 1);
  assert.equal(s.hints, 3);
  assert.deepEqual(s.owned, ['pastel', 'neon']);
  assert.equal(s.theme, 'pastel', 'un skin non possédé ne peut pas être équipé');
  assert.deepEqual(s.stars, {});
  assert.deepEqual(s.daily, {});
  assert.equal(s.noAds, false);
  assert.deepEqual(sanitize(null), defaultSave());
  assert.deepEqual(sanitize([1, 2]), defaultSave());
});
test('sauvegarde : écriture puis relecture, et JSON illisible ignoré', () => {
  const st = memoryStorage();
  assert.ok(writeSave(st, { ...defaultSave(), level: 7 }));
  assert.equal(loadSave(st).level, 7);
  st.setItem(SAVE_KEY, '{pas du json');
  assert.deepEqual(loadSave(st), defaultSave());
});
test('sauvegarde : migration depuis la version 1 du prototype', () => {
  const st = memoryStorage();
  st.setItem('tous-dehors-v1', JSON.stringify({ v: 1, level: 9, done: 8, theme: 'pastel' }));
  const s = loadSave(st);
  assert.equal(s.level, 9);
  assert.equal(s.wins, 8);
});
test('sauvegarde : un stockage bloqué ne casse pas le jeu', () => {
  const broken = { getItem() { throw new Error('bloqué'); }, setItem() { throw new Error('bloqué'); } };
  assert.deepEqual(loadSave(broken), defaultSave());
  assert.equal(writeSave(broken, defaultSave()), false);
});

test('analytics : journalise et nettoie les propriétés', () => {
  const st = memoryStorage(), seen = [];
  const a = createAnalytics({ storage: st, max: 3, sink: e => seen.push(e.name), now: () => 1000 });
  a.track('level_start', { level: 3, obj: { x: 1 }, mode: 'level' });
  assert.deepEqual(a.events()[0], { name: 'level_start', t: 1000, level: 3, mode: 'level' });
  for (let i = 0; i < 5; i++) a.track('level_win', { level: i });
  assert.equal(a.events().length, 3, 'tampon borné');
  assert.equal(seen.length, 6);
  assert.equal(createAnalytics({ storage: st }).events().length, 3, 'relu depuis le stockage');
});
test('analytics : nom invalide refusé, outil externe en panne ignoré', () => {
  const a = createAnalytics({ storage: memoryStorage(), sink: () => { throw new Error('panne'); } });
  assert.throws(() => a.track('Bad Name'), RangeError);
  assert.throws(() => a.track('x'), RangeError);
  assert.doesNotThrow(() => a.track('app_open'));
  a.clear();
  assert.equal(a.events().length, 0);
});

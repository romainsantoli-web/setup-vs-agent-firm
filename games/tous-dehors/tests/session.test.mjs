import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createSession, tap, step, freeCreatures, reviveWithHeart, EXPR } from '../src/game/session.js';
import { levelSpec } from '../src/core/levels.js';
import { mulberry32 } from '../src/core/rng.js';
import { HEARTS } from '../src/core/rules.js';

const run = (s, seconds, dt = 1 / 60) => { const evs = []; for (let t = 0; t < seconds; t += dt) evs.push(...step(s, dt)); return evs; };
const blocked = s => s.list.find(k => k.st === 'idle' && !freeCreatures(s).includes(k));

test('session : un niveau se gagne en ne touchant que des bestioles libres', () => {
  const s = createSession({ spec: levelSpec(12), rnd: mulberry32(1) });
  let now = 0, won = false;
  while (!s.over) {
    const k = freeCreatures(s)[0];
    assert.ok(k, 'aucune bestiole libre alors que le niveau n’est pas fini');
    const evs = tap(s, k.r, k.c, now += 0.2);
    assert.equal(evs[0].type, 'exit');
    if (evs.some(e => e.type === 'win')) won = true;
    run(s, 0.05);
  }
  assert.ok(won);
  assert.equal(s.result, 'win');
  assert.equal(s.left, 0);
  assert.equal(s.mistakes, 0);
});

test('session : une bestiole bloquée se cogne et coûte un cœur', () => {
  const s = createSession({ spec: levelSpec(20), rnd: mulberry32(2) });
  const k = blocked(s);
  assert.ok(k, 'le niveau 20 doit contenir une bestiole bloquée');
  const evs = tap(s, k.r, k.c, 1);
  assert.equal(evs[0].type, 'bump');
  assert.equal(k.expr, EXPR.ouch);
  const later = run(s, 1);
  assert.ok(later.some(e => e.type === 'impact'));
  assert.equal(s.hearts, HEARTS - 1);
  assert.equal(k.st, 'idle', 'la bestiole revient à sa place');
});

test('session : trois bouchons font perdre, une pub rend un cœur', () => {
  const s = createSession({ spec: levelSpec(20), rnd: mulberry32(3) });
  const k = blocked(s);
  let evs = [];
  for (let i = 0; i < HEARTS; i++) { tap(s, k.r, k.c, i); evs = evs.concat(run(s, 1)); }
  assert.ok(evs.some(e => e.type === 'lose'));
  assert.equal(s.result, 'lose');
  assert.deepEqual(tap(s, k.r, k.c, 9), [], 'plus aucune action après la défaite');
  assert.ok(reviveWithHeart(s));
  assert.equal(s.hearts, 1);
  assert.equal(reviveWithHeart(s), false, 'pas de seconde résurrection sans défaite');
});

test('session : le bouclier de série absorbe le premier bouchon', () => {
  const s = createSession({ spec: levelSpec(20), shield: true, rnd: mulberry32(4) });
  const k = blocked(s);
  tap(s, k.r, k.c, 0);
  const evs = run(s, 1);
  assert.ok(evs.find(e => e.type === 'impact').shielded);
  assert.equal(s.hearts, HEARTS);
  tap(s, k.r, k.c, 2); run(s, 1);
  assert.equal(s.hearts, HEARTS - 1);
});

test('session : toucher un rocher, une case vide ou hors grille ne coûte rien', () => {
  const s = createSession({ spec: levelSpec(30), rnd: mulberry32(5) });
  const rock = s.rocks[0];
  assert.ok(rock, 'le niveau 30 contient des rochers');
  assert.equal(tap(s, rock.r, rock.c, 0)[0].type, 'rock');
  assert.deepEqual(tap(s, -1, 0, 0), []);
  assert.deepEqual(tap(s, 0, 99, 0), []);
  assert.equal(s.hearts, HEARTS);
});

test('session : les sorties rapides font monter le combo', () => {
  const s = createSession({ spec: levelSpec(15), rnd: mulberry32(6) });
  const combos = [];
  for (let i = 0; i < 3; i++) { const k = freeCreatures(s)[0]; combos.push(tap(s, k.r, k.c, i * 0.3)[0].combo); }
  assert.deepEqual(combos, [1, 2, 3]);
  const k = freeCreatures(s)[0];
  assert.equal(tap(s, k.r, k.c, 10)[0].combo, 1);
});

test('session : le chrono ne démarre qu’au premier geste', () => {
  const s = createSession({ spec: levelSpec(1), rnd: mulberry32(7) });
  run(s, 1);
  assert.equal(s.time, 0);
  const k = freeCreatures(s)[0];
  tap(s, k.r, k.c, 0); run(s, 0.5);
  assert.ok(s.time > 0.4);
});

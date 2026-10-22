/**
 * Session de jeu : état d'un niveau, règles et animations, sans DOM.
 * tap() et step() renvoient des événements ; le contrôleur (main.js) les traduit
 * en sons, particules et interface. Cette séparation rend toute la logique testable.
 */
import { DIRS, ROCK, isDir, scan } from '../core/grid.js';
import { generateLayout } from '../core/generator.js';
import { mulberry32 } from '../core/rng.js';
import { HEARTS, nextCombo } from '../core/rules.js';

export const EXPR = Object.freeze({ idle: 0, blink: 1, ouch: 2, yay: 3 });

const easeIn = t => t * t * t;
const easeOutBack = t => { const c = 1.9; t -= 1; return 1 + (c + 1) * t * t * t + c * t * t; };

const EXIT_ACCEL = 85, EXIT_MAX = 44, EXIT_START = 7;
const BUMP_IMPACT_S = 0.07, BUMP_RETURN_S = 0.32;

export function createSession({ spec, mode = 'level', shield = false, rnd = Math.random }) {
  const layout = generateLayout(spec, mulberry32(spec.seed));
  const occ = Array.from({ length: layout.rows }, () => Array(layout.cols).fill(null));
  const list = [], rocks = [];
  let id = 0;
  for (let r = 0; r < layout.rows; r++) {
    for (let c = 0; c < layout.cols; c++) {
      const v = layout.cells[r][c];
      if (v === ROCK) { const rock = { rock: true, r, c, wig: 0 }; occ[r][c] = rock; rocks.push(rock); }
      else if (isDir(v)) {
        const k = {
          id: id++, r, c, dir: v, st: 'idle', ox: 0, oy: 0, v: 0, dist: 0, t: 0, d: 0, hit: false, blocker: null,
          press: 0, wig: 0, expr: EXPR.idle, exprT: 0, blink: 1 + rnd() * 4, seed: rnd() * 10,
          spawn: (r + c) * 0.035 + rnd() * 0.08, crossed: false, dead: false,
        };
        occ[r][c] = k; list.push(k);
      }
    }
  }
  return {
    mode, spec, rows: layout.rows, cols: layout.cols, occ, list, rocks,
    total: list.length, left: list.length, hearts: HEARTS, mistakes: 0, time: 0,
    started: false, over: false, result: null, combo: 0, lastExit: -99, shield, rnd,
  };
}

/** Bestioles qui peuvent sortir immédiatement (pour les indices et le tutoriel). */
export function freeCreatures(s) {
  return s.list.filter(k => k.st === 'idle' && scan(s.occ, k.r, k.c, k.dir) === null);
}

/** Le joueur touche la case (r, c) à l'instant now (secondes). */
export function tap(s, r, c, now) {
  if (s.over || r < 0 || r >= s.rows || c < 0 || c >= s.cols) return [];
  const k = s.occ[r][c];
  if (!k) return [];
  if (k.rock) { k.wig = 1; return [{ type: 'rock', rock: k }]; }
  if (k.st !== 'idle') return [];
  s.started = true;
  const blk = scan(s.occ, r, c, k.dir);
  if (blk === null) {
    s.occ[r][c] = null; s.left--;
    k.st = 'exit'; k.v = EXIT_START; k.dist = 0; k.expr = EXPR.yay; k.exprT = 99; k.press = 1;
    s.combo = nextCombo(s.combo, s.lastExit, now); s.lastExit = now;
    const evs = [{ type: 'exit', k, combo: s.combo }];
    if (s.left === 0) { s.over = true; s.result = 'win'; evs.push({ type: 'win' }); }
    return evs;
  }
  k.st = 'bump'; k.t = 0; k.d = blk.dist; k.blocker = blk.cell; k.hit = false; k.expr = EXPR.ouch; k.exprT = 0.9;
  return [{ type: 'bump', k }];
}

/** Avance la simulation de dt secondes. */
export function step(s, dt) {
  const evs = [];
  if (s.started && !s.over) s.time += dt;
  for (const rock of s.rocks) if (rock.wig > 0) rock.wig = Math.max(0, rock.wig - dt * 3);
  for (const k of s.list) {
    if (k.exprT > 0) { k.exprT -= dt; if (k.exprT <= 0) k.expr = EXPR.idle; }
    if (k.st === 'idle') {
      k.blink -= dt;
      if (k.blink < 0) { if (k.expr === EXPR.idle) { k.expr = EXPR.blink; k.exprT = 0.12; } k.blink = 2 + s.rnd() * 5; }
    }
    if (k.press > 0) k.press = Math.max(0, k.press - dt * 5);
    if (k.wig > 0) k.wig = Math.max(0, k.wig - dt * 2.6);
    const [dr, dc] = DIRS[k.dir];

    if (k.st === 'exit') {
      k.v = Math.min(EXIT_MAX, k.v + EXIT_ACCEL * dt);
      k.dist += k.v * dt; k.ox = dc * k.dist; k.oy = dr * k.dist;
      const x = k.c + 0.5 + k.ox, y = k.r + 0.5 + k.oy;
      if (!k.crossed && (x < 0 || x > s.cols || y < 0 || y > s.rows)) { k.crossed = true; evs.push({ type: 'cross', k }); }
      if (x < -3 || x > s.cols + 3 || y < -3 || y > s.rows + 3) k.dead = true;
    } else if (k.st === 'bump') {
      k.t += dt;
      const go = 0.06 + 0.045 * k.d, far = k.d + 0.22;
      let p;
      if (k.t < go) p = easeIn(k.t / go) * far;
      else if (k.t < go + BUMP_IMPACT_S) {
        p = far;
        if (!k.hit) {
          k.hit = true; k.press = 1;
          const b = k.blocker; b.wig = 1;
          if (!b.rock) { b.expr = EXPR.ouch; b.exprT = 0.7; }
          const shielded = s.shield;
          if (shielded) s.shield = false;
          else { s.hearts--; s.mistakes++; }
          evs.push({ type: 'impact', k, blocker: b, shielded });
          if (!s.over && s.hearts <= 0) { s.over = true; s.result = 'lose'; evs.push({ type: 'lose' }); }
        }
      } else if (k.t < go + BUMP_IMPACT_S + BUMP_RETURN_S) p = far * (1 - easeOutBack((k.t - go - BUMP_IMPACT_S) / BUMP_RETURN_S));
      else { p = 0; k.st = 'idle'; }
      k.ox = dc * p; k.oy = dr * p;
    }
  }
  if (s.list.some(k => k.dead)) s.list = s.list.filter(k => !k.dead);
  return evs;
}

/** Rendre un cœur après une pub récompensée. */
export function reviveWithHeart(s) {
  if (s.result !== 'lose') return false;
  s.hearts = 1; s.over = false; s.result = null;
  return true;
}

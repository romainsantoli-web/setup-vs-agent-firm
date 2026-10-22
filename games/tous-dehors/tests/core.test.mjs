import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, shuffle, dayKey } from '../src/core/rng.js';
import { DIRS, ROCK, isDir, scan } from '../src/core/grid.js';
import { generateLayout, solve, validateParams } from '../src/core/generator.js';
import { levelSpec, chapterOf, dailySpec, assertLevel, MAX_COLS, MAX_ROWS, ROCKS_FROM_LEVEL } from '../src/core/levels.js';
import { starsFor, nextCombo, streakAfter, hasShield, rankFor, totalStars, RANKS } from '../src/core/rules.js';
import { shouldShowInterstitial, hintsForWin, dailyRotation, eventWindow, HALLOWEEN, formatEur } from '../src/core/economy.js';

test('rng : même seed, même suite ; seeds différents, suites différentes', () => {
  const a = mulberry32(42), b = mulberry32(42), c = mulberry32(43);
  const sa = [a(), a(), a()], sb = [b(), b(), b()], sc = [c(), c(), c()];
  assert.deepEqual(sa, sb);
  assert.notDeepEqual(sa, sc);
  for (const v of sa) assert.ok(v >= 0 && v < 1);
});
test('rng : seed invalide refusé', () => {
  assert.throws(() => mulberry32(NaN), TypeError);
  assert.throws(() => mulberry32(Infinity), TypeError);
});
test('shuffle garde les mêmes éléments ; dayKey au format AAAAMMJJ', () => {
  const arr = shuffle([1, 2, 3, 4, 5], mulberry32(1));
  assert.deepEqual([...arr].sort(), [1, 2, 3, 4, 5]);
  assert.equal(dayKey(new Date(2026, 9, 22)), 20261022);
});

test('grille : scan trouve l’obstacle et la distance', () => {
  const cells = [[1, null, null, 3]];
  assert.deepEqual(scan(cells, 0, 0, 1), { r: 0, c: 3, dist: 2, cell: 3 });
  assert.equal(scan(cells, 0, 3, 1), null);
  assert.ok(isDir(0) && isDir(3));
  assert.ok(!isDir(4) && !isDir(-1) && !isDir(1.5) && !isDir(ROCK));
  assert.equal(DIRS.length, 4);
});

test('générateur : 300 niveaux générés sont tous solubles', () => {
  for (let L = 1; L <= 300; L++) {
    const spec = levelSpec(L);
    const lay = generateLayout(spec, mulberry32(spec.seed));
    assert.equal(lay.rows, spec.rows);
    assert.equal(lay.rocks, spec.rocks);
    assert.ok(solve(lay).solved, `niveau ${L} insoluble`);
  }
});
test('générateur : la densité visée est presque atteinte', () => {
  const spec = { rows: 8, cols: 8, density: 0.85, rocks: 0, seed: 7 };
  const lay = generateLayout(spec, mulberry32(7));
  assert.ok(lay.creatures >= Math.round(64 * 0.85) * 0.85, `seulement ${lay.creatures} bestioles`);
});
test('générateur : même seed, même grille', () => {
  const spec = levelSpec(23);
  assert.deepEqual(generateLayout(spec, mulberry32(spec.seed)).cells, generateLayout(spec, mulberry32(spec.seed)).cells);
});
test('générateur : paramètres invalides refusés', () => {
  assert.throws(() => validateParams({ rows: 1, cols: 4, density: 0.5 }), RangeError);
  assert.throws(() => validateParams({ rows: 4, cols: 40, density: 0.5 }), RangeError);
  assert.throws(() => validateParams({ rows: 4, cols: 4, density: 0 }), RangeError);
  assert.throws(() => validateParams({ rows: 4, cols: 4, density: 1.5 }), RangeError);
  assert.throws(() => validateParams({ rows: 4, cols: 4, density: 0.5, rocks: 99 }), RangeError);
  assert.throws(() => validateParams({ rows: 4.5, cols: 4, density: 0.5 }), RangeError);
});
test('solveur : détecte une grille insoluble', () => {
  // deux bestioles face à face : aucune ne peut sortir
  const lay = { rows: 1, cols: 2, cells: [[1, 3]] };
  assert.equal(solve(lay).solved, false);
  // un rocher bloque la seule sortie
  assert.equal(solve({ rows: 1, cols: 2, cells: [[1, ROCK]] }).solved, false);
  assert.equal(solve({ rows: 1, cols: 2, cells: [[3, ROCK]] }).solved, true);
});

test('niveaux : tailles bornées, dents de scie, rochers dès le niveau 8', () => {
  for (let L = 1; L <= 500; L++) {
    const s = levelSpec(L);
    assert.ok(s.cols <= MAX_COLS && s.rows <= MAX_ROWS && s.cols >= 4);
    assert.ok(s.density > 0 && s.density <= 0.95);
    assert.equal(s.rocks > 0, L >= ROCKS_FROM_LEVEL);
  }
  assert.ok(levelSpec(10).hard && !levelSpec(9).hard);
  assert.ok(levelSpec(11).breather && levelSpec(11).density < levelSpec(10).density);
  assert.equal(levelSpec(4).rocks, 0);
});
test('niveaux : numéros invalides refusés', () => {
  for (const bad of [0, -1, 1.5, NaN, '3', 100001]) assert.throws(() => assertLevel(bad), RangeError);
  assert.throws(() => levelSpec(0), RangeError);
  assert.throws(() => chapterOf(-5), RangeError);
});
test('chapitres : 10 niveaux par chapitre', () => {
  assert.deepEqual([chapterOf(1).number, chapterOf(10).number, chapterOf(11).number], [1, 1, 2]);
  assert.equal(chapterOf(11).name, 'Le Métro');
  assert.equal(chapterOf(15).position, 5);
  assert.equal(chapterOf(101).name, 'Le Salon');
});
test('défi du jour : spec valide, clé invalide refusée', () => {
  const s = dailySpec(20261022);
  assert.equal(s.seed, 20261022);
  assert.ok(solve(generateLayout(s, mulberry32(s.seed))).solved);
  assert.throws(() => dailySpec(123), RangeError);
  assert.throws(() => dailySpec('20261022'), RangeError);
});

test('règles : étoiles, combos, séries, bouclier', () => {
  assert.deepEqual([starsFor(0), starsFor(1), starsFor(2), starsFor(9)], [3, 2, 1, 1]);
  assert.equal(nextCombo(2, 10, 10.5), 3);
  assert.equal(nextCombo(5, 10, 11), 1);
  assert.equal(streakAfter(2, true), 3);
  assert.equal(streakAfter(7, false), 0);
  assert.ok(hasShield(3) && !hasShield(2));
});
test('règles : valeurs invalides refusées', () => {
  assert.throws(() => starsFor(-1), RangeError);
  assert.throws(() => starsFor(1.2), RangeError);
  assert.throws(() => streakAfter(-1, true), RangeError);
  assert.throws(() => hasShield(NaN), RangeError);
  assert.throws(() => rankFor(-3), RangeError);
});
test('rangs : progression avec les étoiles', () => {
  assert.equal(rankFor(0).name, RANKS[0].name);
  assert.equal(rankFor(15).name, RANKS[1].name);
  assert.equal(rankFor(10000).next, null);
  assert.equal(totalStars({ 1: 3, 2: 2, 3: 9, 4: 'x' }), 5);
  assert.equal(totalStars(null), 0);
});

test('pubs : jamais avant le niveau 11, au plus une tous les 3 niveaux, jamais avec « sans pub »', () => {
  assert.equal(shouldShowInterstitial({ level: 5, wins: 3, noAds: false }), false);
  assert.equal(shouldShowInterstitial({ level: 10, wins: 9, noAds: false }), false);
  assert.equal(shouldShowInterstitial({ level: 12, wins: 12, noAds: false }), true);
  assert.equal(shouldShowInterstitial({ level: 12, wins: 13, noAds: false }), false);
  assert.equal(shouldShowInterstitial({ level: 40, wins: 39, noAds: true }), false);
});
test('pubs : entrées invalides refusées', () => {
  assert.throws(() => shouldShowInterstitial({ level: 0, wins: 3 }), RangeError);
  assert.throws(() => shouldShowInterstitial({ level: 12, wins: -1 }), RangeError);
});
test('indices : un indice offert toutes les 3 victoires', () => {
  assert.deepEqual([1, 2, 3, 4, 5, 6].map(hintsForWin), [0, 0, 1, 0, 0, 1]);
  assert.throws(() => hintsForWin(0), RangeError);
});
test('boutique : rotation déterministe, sans skin gratuit ni événementiel', () => {
  const themes = { a: { price: 0 }, b: { price: 1 }, c: { price: 1 }, d: { price: 1, event: true }, e: { price: 2 }, f: { price: 1 } };
  const r1 = dailyRotation(themes, mulberry32(20261022)), r2 = dailyRotation(themes, mulberry32(20261022));
  assert.deepEqual(r1, r2);
  assert.equal(r1.length, 3);
  assert.ok(!r1.includes('a') && !r1.includes('d'));
  assert.deepEqual(dailyRotation(themes, mulberry32(1), -2), []);
});
test('événement Halloween : actif en octobre seulement', () => {
  assert.equal(eventWindow(new Date(2026, 9, 22), HALLOWEEN).active, true);
  assert.equal(eventWindow(new Date(2026, 10, 1), HALLOWEEN).active, false);
  assert.match(formatEur(1.99), /1,99/);
});

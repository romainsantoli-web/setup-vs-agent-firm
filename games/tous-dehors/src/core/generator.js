/**
 * Génération de niveaux toujours solubles.
 *
 * Construction à rebours : on pose les bestioles une à une, et chacune doit avoir
 * une sortie libre au moment où on la pose. L'ordre inverse de pose est donc une
 * solution garantie. Les rochers sont posés en premier et ne bougent jamais.
 */
import { ROCK, isDir, scan } from './grid.js';
import { shuffle } from './rng.js';

export const LIMITS = Object.freeze({ minSide: 2, maxSide: 12, maxRockRatio: 0.25 });

export function validateParams({ rows, cols, density, rocks = 0 }) {
  const side = v => Number.isInteger(v) && v >= LIMITS.minSide && v <= LIMITS.maxSide;
  if (!side(rows) || !side(cols)) throw new RangeError(`taille invalide : ${rows}×${cols}`);
  if (!(typeof density === 'number' && density > 0 && density <= 1)) throw new RangeError(`densité invalide : ${density}`);
  if (!Number.isInteger(rocks) || rocks < 0 || rocks > Math.floor(rows * cols * LIMITS.maxRockRatio)) throw new RangeError(`nombre de rochers invalide : ${rocks}`);
}

/**
 * @returns {{ rows:number, cols:number, cells:(number|null)[][], creatures:number, rocks:number }}
 *   cells[r][c] vaut null (vide), ROCK, ou une direction 0..3.
 */
export function generateLayout(params, rnd) {
  validateParams(params);
  const { rows, cols, density, rocks = 0 } = params;
  const cells = Array.from({ length: rows }, () => Array(cols).fill(null));
  const all = [];
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) all.push([r, c]);

  shuffle(all, rnd);
  let placedRocks = 0;
  for (const [r, c] of all) {
    if (placedRocks >= rocks) break;
    cells[r][c] = ROCK;
    placedRocks++;
  }

  const target = Math.round((rows * cols - placedRocks) * density);
  let placed = 0;
  for (let pass = 0; pass < 4 && placed < target; pass++) {
    shuffle(all, rnd);
    for (const [r, c] of all) {
      if (placed >= target) break;
      if (cells[r][c] !== null) continue;
      const dirs = shuffle([0, 1, 2, 3], rnd);
      for (const d of dirs) {
        if (scan(cells, r, c, d) === null) { cells[r][c] = d; placed++; break; }
      }
    }
  }
  return { rows, cols, cells, creatures: placed, rocks: placedRocks };
}

/**
 * Solveur glouton. Faire sortir une bestiole libre ne bloque jamais les autres :
 * le glouton résout donc toute grille soluble. Sert aux tests et aux indices.
 * @returns {{ solved:boolean, order:[number, number][] }}
 */
export function solve(layout) {
  const cells = layout.cells.map(row => row.slice());
  const order = [];
  let progress = true;
  while (progress) {
    progress = false;
    for (let r = 0; r < layout.rows; r++) {
      for (let c = 0; c < layout.cols; c++) {
        const v = cells[r][c];
        if (isDir(v) && scan(cells, r, c, v) === null) {
          cells[r][c] = null;
          order.push([r, c]);
          progress = true;
        }
      }
    }
  }
  const left = cells.flat().filter(isDir).length;
  return { solved: left === 0, order };
}

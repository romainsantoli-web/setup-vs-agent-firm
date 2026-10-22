/**
 * Courbe de difficulté, chapitres et paramètres de chaque niveau.
 *
 * Principes (repris des leaders du puzzle mobile) :
 * - progression lente de la taille de grille et de la densité ;
 * - courbe en dents de scie : un niveau « difficile » tous les 5 niveaux,
 *   suivi d'un niveau « respiration » plus facile ;
 * - une nouvelle mécanique introduite régulièrement (les rochers au niveau 8).
 */
export const MAX_COLS = 8;
export const MAX_ROWS = 10;
export const LEVELS_PER_CHAPTER = 10;
export const MAX_LEVEL = 100000;
export const ROCKS_FROM_LEVEL = 8;

export const CHAPTERS = Object.freeze([
  'Le Salon', 'Le Métro', 'Le Bureau', 'La Plage', 'Le Concert',
  'L’Aéroport', 'La Cantine', 'Le Festival', 'Le Stade', 'La Lune',
]);

export function assertLevel(level) {
  if (!Number.isInteger(level) || level < 1 || level > MAX_LEVEL) {
    throw new RangeError(`niveau invalide : ${level}`);
  }
}

/** Chapitre d'un niveau ; les noms bouclent après le dernier chapitre. */
export function chapterOf(level) {
  assertLevel(level);
  const index = Math.floor((level - 1) / LEVELS_PER_CHAPTER);
  const first = index * LEVELS_PER_CHAPTER + 1;
  return {
    number: index + 1,
    name: CHAPTERS[index % CHAPTERS.length],
    first,
    last: first + LEVELS_PER_CHAPTER - 1,
    position: level - first + 1,
  };
}

export function levelSpec(level) {
  assertLevel(level);
  const cols = Math.min(MAX_COLS, 4 + Math.floor((level - 1) / 3));
  const rows = Math.min(MAX_ROWS, cols + Math.min(2, Math.floor((level - 1) / 4)));
  const hard = level >= 5 && level % 5 === 0;
  const breather = level > 5 && level % 5 === 1;
  let density = Math.min(0.9, 0.52 + level * 0.028);
  if (hard) density = Math.min(0.95, density + 0.05);
  if (breather) density = Math.max(0.5, density - 0.08);
  const rockCap = Math.floor(rows * cols * 0.12);
  const rocks = level >= ROCKS_FROM_LEVEL ? Math.min(rockCap, 6, 1 + Math.floor((level - ROCKS_FROM_LEVEL) / 6)) : 0;
  return { level, rows, cols, density, rocks, hard, breather, seed: level * 7919 + 13 };
}

/** Défi du jour : grande grille dense, identique pour tous les joueurs ce jour-là. */
export function dailySpec(key) {
  if (!Number.isInteger(key) || key < 20000101 || key > 99991231) throw new RangeError(`clé de jour invalide : ${key}`);
  return { level: 0, rows: MAX_ROWS, cols: MAX_COLS, density: 0.9, rocks: 3, hard: true, breather: false, seed: key };
}

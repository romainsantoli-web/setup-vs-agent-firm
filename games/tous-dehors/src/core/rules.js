/**
 * Règles de score et de progression, sans effet de bord.
 */
export const HEARTS = 3;
export const COMBO_WINDOW_S = 0.75;
export const STREAK_FOR_SHIELD = 3;

export const RANKS = Object.freeze([
  { stars: 0, name: 'Stagiaire de l’évacuation' },
  { stars: 15, name: 'Agent de sortie' },
  { stars: 45, name: 'Chef de gare' },
  { stars: 90, name: 'Maître des portes' },
  { stars: 150, name: 'Bison Futé' },
  { stars: 240, name: 'Légende du dehors' },
]);

const assertCount = (v, name) => {
  if (!Number.isInteger(v) || v < 0) throw new RangeError(`${name} invalide : ${v}`);
};

/** 0 erreur : 3 étoiles ; 1 erreur : 2 étoiles ; au-delà : 1 étoile. */
export function starsFor(mistakes) {
  assertCount(mistakes, 'mistakes');
  return mistakes === 0 ? 3 : mistakes === 1 ? 2 : 1;
}

/** Combo : les sorties enchaînées en moins de COMBO_WINDOW_S secondes s'additionnent. */
export function nextCombo(combo, lastExitAt, now) {
  return now - lastExitAt < COMBO_WINDOW_S ? combo + 1 : 1;
}

/** Série de victoires : toute défaite la remet à zéro. */
export function streakAfter(streak, won) {
  assertCount(streak, 'streak');
  return won ? streak + 1 : 0;
}

/** À partir de 3 victoires d'affilée, le premier bouchon du niveau est gratuit. */
export function hasShield(streak) {
  assertCount(streak, 'streak');
  return streak >= STREAK_FOR_SHIELD;
}

export function totalStars(starsByLevel) {
  return Object.values(starsByLevel || {}).reduce((s, v) => s + (Number.isInteger(v) && v > 0 && v <= 3 ? v : 0), 0);
}

export function rankFor(stars) {
  assertCount(stars, 'stars');
  let i = 0;
  while (i + 1 < RANKS.length && stars >= RANKS[i + 1].stars) i++;
  return { name: RANKS[i].name, level: i + 1, next: RANKS[i + 1] || null };
}

/**
 * Générateurs pseudo-aléatoires déterministes.
 * Un même seed produit toujours la même grille : indispensable pour le défi du jour
 * (même grille pour tous les joueurs) et pour rejouer un niveau à l'identique.
 */

/** Mulberry32 : rapide, 32 bits, largement suffisant pour du level design. */
export function mulberry32(seed) {
  if (!Number.isFinite(seed)) throw new TypeError('seed doit être un nombre fini');
  let a = seed | 0;
  return function next() {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Mélange de Fisher-Yates, en place. */
export function shuffle(arr, rnd) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

/** Clé de jour locale AAAAMMJJ, utilisée comme seed du défi du jour et de la boutique. */
export function dayKey(d = new Date()) {
  return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
}

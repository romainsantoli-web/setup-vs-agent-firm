/**
 * Géométrie de la grille, partagée par le générateur et la session de jeu.
 * Directions : 0 haut, 1 droite, 2 bas, 3 gauche, exprimées en [dLigne, dColonne].
 */
export const DIRS = Object.freeze([
  Object.freeze([-1, 0]),
  Object.freeze([0, 1]),
  Object.freeze([1, 0]),
  Object.freeze([0, -1]),
]);

/** Valeur d'une case rocher dans une disposition générée. */
export const ROCK = -1;

export function isDir(d) {
  return Number.isInteger(d) && d >= 0 && d <= 3;
}

/**
 * Parcourt la ligne de sortie depuis (r, c) dans la direction dir.
 * Retourne null si la voie est libre jusqu'au bord, sinon { r, c, dist, cell }
 * où dist est le nombre de cases vides avant l'obstacle.
 */
export function scan(cells, r, c, dir) {
  const rows = cells.length, cols = cells[0].length;
  const [dr, dc] = DIRS[dir];
  let dist = 0;
  for (let y = r + dr, x = c + dc; y >= 0 && y < rows && x >= 0 && x < cols; y += dr, x += dc, dist++) {
    const v = cells[y][x];
    if (v !== null && v !== undefined) return { r: y, c: x, dist, cell: v };
  }
  return null;
}

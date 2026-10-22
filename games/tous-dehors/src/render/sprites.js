/**
 * Dessin vectoriel des bestioles et des rochers, pré-rendu dans des canvas hors écran.
 * Chaque combinaison (skin, direction, expression, taille) n'est dessinée qu'une fois :
 * le plateau ne fait ensuite que des drawImage, ce qui garde 60 images/seconde.
 */
import { DIRS } from '../core/grid.js';
import { EXPR } from '../game/session.js';
import { shade } from './gl.js';

const TAU = Math.PI * 2;
const INK = '#24123a';

export function drawCreature(c, s, theme, dir, expr) {
  const col = theme.dirs[dir], [vy, vx] = DIRS[dir], px = -vy, py = vx;
  c.lineCap = 'round'; c.lineJoin = 'round';
  // ombre portée
  c.fillStyle = 'rgba(0,0,0,.26)';
  c.beginPath(); c.ellipse(0, s * .37, s * .27, s * .065, 0, 0, TAU); c.fill();
  // nez-flèche
  const tip = [vx * s * .5, vy * s * .5];
  const b1 = [vx * s * .15 + px * s * .22, vy * s * .15 + py * s * .22];
  const b2 = [vx * s * .15 - px * s * .22, vy * s * .15 - py * s * .22];
  c.fillStyle = c.strokeStyle = shade(col, -.2); c.lineWidth = s * .11;
  c.beginPath(); c.moveTo(tip[0], tip[1]); c.lineTo(b1[0], b1[1]); c.lineTo(b2[0], b2[1]); c.closePath(); c.fill(); c.stroke();
  // corps
  const g = c.createRadialGradient(-s * .12, -s * .15, s * .03, 0, 0, s * .4);
  g.addColorStop(0, shade(col, .45)); g.addColorStop(.55, col); g.addColorStop(1, shade(col, -.22));
  c.fillStyle = g; c.beginPath(); c.arc(0, 0, s * .34, 0, TAU); c.fill();
  c.strokeStyle = 'rgba(255,255,255,.35)'; c.lineWidth = s * .025;
  c.beginPath(); c.arc(0, 0, s * .32, Math.PI * 1.05, Math.PI * 1.55); c.stroke();
  // chevron de direction
  c.strokeStyle = 'rgba(255,255,255,.85)'; c.lineWidth = s * .05;
  const ch = (k, w) => [vx * s * k + px * s * w, vy * s * k + py * s * w];
  const q1 = ch(.33, .08), q2 = ch(.41, 0), q3 = ch(.33, -.08);
  c.beginPath(); c.moveTo(q1[0], q1[1]); c.lineTo(q2[0], q2[1]); c.lineTo(q3[0], q3[1]); c.stroke();
  // accessoires de skin
  if (theme.stem) {
    c.fillStyle = '#3f6212'; c.fillRect(-s * .04, -s * .45, s * .08, s * .14);
    c.fillStyle = '#65a30d'; c.beginPath(); c.ellipse(s * .09, -s * .41, s * .08, s * .035, -.5, 0, TAU); c.fill();
  }
  // joues
  c.fillStyle = 'rgba(255,120,150,.38)';
  for (const sx of [-1, 1]) { c.beginPath(); c.ellipse(sx * s * .2, s * .07, s * .055, s * .035, 0, 0, TAU); c.fill(); }
  const ex = s * .115, ey = -s * .04;
  if (theme.mask) { c.fillStyle = '#111'; c.beginPath(); c.ellipse(0, ey, s * .25, s * .1, 0, 0, TAU); c.fill(); }
  // yeux
  c.strokeStyle = INK; c.fillStyle = INK; c.lineWidth = s * .035;
  if (expr === EXPR.blink) {
    for (const sx of [-1, 1]) { c.beginPath(); c.arc(sx * ex, ey, s * .05, Math.PI * .15, Math.PI * .85); c.stroke(); }
  } else if (expr === EXPR.ouch) {
    for (const sx of [-1, 1]) {
      c.beginPath(); c.moveTo(sx * ex - s * .045 * sx, ey - s * .045); c.lineTo(sx * ex + s * .04 * sx, ey); c.lineTo(sx * ex - s * .045 * sx, ey + s * .045); c.stroke();
    }
  } else if (expr === EXPR.yay) {
    for (const sx of [-1, 1]) { c.beginPath(); c.arc(sx * ex, ey + s * .02, s * .05, Math.PI * 1.15, Math.PI * 1.85); c.stroke(); }
  } else {
    for (const sx of [-1, 1]) {
      c.fillStyle = '#fff'; c.beginPath(); c.ellipse(sx * ex, ey, s * .072, s * .088, 0, 0, TAU); c.fill();
      c.fillStyle = INK; c.beginPath(); c.arc(sx * ex + vx * s * .028, ey + vy * s * .032, s * .045, 0, TAU); c.fill();
      c.fillStyle = '#fff'; c.beginPath(); c.arc(sx * ex + vx * s * .028 - s * .015, ey + vy * s * .032 - s * .018, s * .014, 0, TAU); c.fill();
    }
  }
  // bouche
  c.fillStyle = INK;
  if (expr === EXPR.ouch) { c.beginPath(); c.ellipse(0, s * .12, s * .045, s * .055, 0, 0, TAU); c.fill(); }
  else if (expr === EXPR.yay) {
    c.beginPath(); c.arc(0, s * .08, s * .09, 0, Math.PI); c.closePath(); c.fill();
    c.fillStyle = '#ff6b8b'; c.beginPath(); c.ellipse(0, s * .14, s * .045, s * .025, 0, 0, TAU); c.fill();
  } else { c.lineWidth = s * .035; c.beginPath(); c.arc(0, s * .07, s * .055, Math.PI * .15, Math.PI * .85); c.stroke(); }
}

export function drawRock(c, s) {
  c.fillStyle = 'rgba(0,0,0,.28)';
  c.beginPath(); c.ellipse(0, s * .34, s * .32, s * .07, 0, 0, TAU); c.fill();
  const pts = [[-.38, .22], [-.34, -.12], [-.12, -.34], [.18, -.3], [.38, -.06], [.36, .24], [.05, .32]];
  const g = c.createLinearGradient(0, -s * .35, 0, s * .32);
  g.addColorStop(0, '#9aa3b5'); g.addColorStop(1, '#4b5263');
  c.fillStyle = g; c.strokeStyle = '#3a3f4d'; c.lineWidth = s * .05; c.lineJoin = 'round';
  c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x * s, y * s) : c.moveTo(x * s, y * s))); c.closePath(); c.fill(); c.stroke();
  c.strokeStyle = 'rgba(255,255,255,.28)'; c.lineWidth = s * .04;
  c.beginPath(); c.moveTo(-s * .22, -s * .16); c.lineTo(-s * .05, -s * .26); c.stroke();
  c.strokeStyle = 'rgba(0,0,0,.25)';
  c.beginPath(); c.moveTo(s * .05, s * .05); c.lineTo(s * .2, -s * .08); c.moveTo(s * .05, s * .05); c.lineTo(s * .02, s * .2); c.stroke();
}

export function createSpriteCache() {
  const cache = new Map();
  function make(key, sizePx, draw) {
    let cnv = cache.get(key);
    if (cnv) return cnv;
    const S = Math.ceil(sizePx * 1.3);
    cnv = document.createElement('canvas'); cnv.width = cnv.height = S;
    const c = cnv.getContext('2d'); c.translate(S / 2, S / 2); draw(c);
    cache.set(key, cnv);
    return cnv;
  }
  return {
    creature: (theme, dir, expr, sizePx) => make(`${theme.name}|${dir}|${expr}|${sizePx}`, sizePx, c => drawCreature(c, sizePx, theme, dir, expr)),
    rock: sizePx => make(`rock|${sizePx}`, sizePx, c => drawRock(c, sizePx)),
    clear: () => cache.clear(),
  };
}

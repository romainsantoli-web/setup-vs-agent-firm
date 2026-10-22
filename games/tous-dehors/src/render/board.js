/**
 * Rendu Canvas 2D du plateau : verre, bestioles, rochers, indice, textes flottants.
 * Lit l'état de la session sans jamais le modifier.
 */
import { createSpriteCache } from './sprites.js';

const TAU = Math.PI * 2;
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const easeOutBack = t => { const c = 1.9; t -= 1; return 1 + (c + 1) * t * t * t + c * t * t; };

function roundRect(c, x, y, w, h, r) {
  c.beginPath(); c.moveTo(x + r, y);
  c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r);
  c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath();
}

export function createBoardRenderer(canvas, { reducedMotion = false } = {}) {
  const ctx = canvas.getContext('2d', { alpha: true });
  const sprites = createSpriteCache();
  const view = { W: 300, H: 300, dpr: 1, cs: 40, bx: 0, by: 0, bw: 0, bh: 0, rect: { left: 0, top: 0 } };

  function layout(rows, cols) {
    const parent = canvas.parentElement;
    view.W = Math.max(100, parent.clientWidth); view.H = Math.max(100, parent.clientHeight);
    view.dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(view.W * view.dpr); canvas.height = Math.round(view.H * view.dpr);
    if (rows && cols) {
      view.cs = Math.floor(Math.min((view.W - 12) / cols, (view.H - 12) / rows, 74));
      view.bw = view.cs * cols; view.bh = view.cs * rows;
      view.bx = Math.round((view.W - view.bw) / 2); view.by = Math.round((view.H - view.bh) / 2);
    }
    sprites.clear();
    view.rect = canvas.getBoundingClientRect();
  }

  const kx = k => view.bx + (k.c + 0.5 + (k.ox || 0)) * view.cs;
  const ky = k => view.by + (k.r + 0.5 + (k.oy || 0)) * view.cs;
  const toViewport = (x, y) => [view.rect.left + x, view.rect.top + y];
  function cellAt(clientX, clientY) {
    const x = clientX - view.rect.left, y = clientY - view.rect.top;
    return { r: Math.floor((y - view.by) / view.cs), c: Math.floor((x - view.bx) / view.cs) };
  }

  function draw(s, theme, T, { floats = [], hint = null, shake = 0, age = 0 } = {}) {
    const { W, H, dpr, cs, bx, by, bw, bh } = view;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    if (shake) ctx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);

    const pad = Math.max(6, cs * 0.14);
    roundRect(ctx, bx - pad, by - pad, bw + pad * 2, bh + pad * 2, Math.max(14, cs * 0.38));
    ctx.fillStyle = 'rgba(255,255,255,.075)'; ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,.14)'; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,.10)';
    for (let r = 0; r < s.rows; r++) for (let c = 0; c < s.cols; c++) {
      ctx.beginPath(); ctx.arc(bx + (c + 0.5) * cs, by + (r + 0.5) * cs, Math.max(1.5, cs * 0.045), 0, TAU); ctx.fill();
    }

    const px = Math.round(cs * dpr);
    const rockSpr = sprites.rock(px), RS = rockSpr.width / dpr;
    for (const rock of s.rocks) {
      const rot = rock.wig > 0 ? Math.sin(rock.wig * 40) * 0.08 * rock.wig : 0;
      ctx.save(); ctx.translate(bx + (rock.c + 0.5) * cs, by + (rock.r + 0.5) * cs); if (rot) ctx.rotate(rot);
      ctx.drawImage(rockSpr, -RS / 2, -RS / 2, RS, RS); ctx.restore();
    }

    if (hint && hint.st === 'idle') {
      const a = 0.5 + 0.5 * Math.sin(T * 8);
      ctx.strokeStyle = `rgba(255,214,90,${0.45 + 0.45 * a})`; ctx.lineWidth = 3 + a * 2;
      ctx.beginPath(); ctx.arc(kx(hint), ky(hint), cs * (0.46 + 0.05 * a), 0, TAU); ctx.stroke();
    }

    const drawK = k => {
      const sp = clamp((age - k.spawn) / 0.38, 0, 1);
      if (sp <= 0) return;
      const pop = reducedMotion ? 1 : easeOutBack(sp);
      const spr = sprites.creature(theme, k.dir, k.expr, px), S = spr.width / dpr;
      let sx = 1, sy = 1, rot = 0, y = ky(k);
      if (k.st === 'idle' && !reducedMotion) y += Math.sin(T * 2.4 + k.seed) * cs * 0.025;
      if (k.st === 'exit') {
        const st = 1 + Math.min(0.38, k.v * 0.012);
        if (k.dir % 2) { sx = st; sy = 1 / st; } else { sx = 1 / st; sy = st; }
      }
      const sq = k.press * 0.14; sx *= (1 + sq) * pop; sy *= (1 - sq) * pop;
      if (k.wig > 0) rot = Math.sin(k.wig * 30) * 0.22 * k.wig;
      ctx.save(); ctx.translate(kx(k), y); if (rot) ctx.rotate(rot); ctx.scale(sx, sy);
      ctx.drawImage(spr, -S / 2, -S / 2, S, S); ctx.restore();
    };
    for (const k of s.list) if (k.st !== 'exit') drawK(k);
    for (const k of s.list) if (k.st === 'exit') drawK(k);

    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    for (const f of floats) {
      ctx.globalAlpha = clamp(f.life * 1.6, 0, 1);
      ctx.font = `700 ${Math.round(f.size)}px Fredoka, "Arial Rounded MT Bold", sans-serif`;
      const tw = ctx.measureText(f.text).width, x = clamp(f.x, tw / 2 + 8, W - tw / 2 - 8);
      ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(20,8,40,.85)'; ctx.strokeText(f.text, x, f.y);
      ctx.fillStyle = f.col; ctx.fillText(f.text, x, f.y);
    }
    ctx.globalAlpha = 1;
  }

  return { view, layout, draw, kx, ky, toViewport, cellAt, sprites };
}

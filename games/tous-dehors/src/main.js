/**
 * Contrôleur de l'application : écrans, boucle d'animation, liaison logique ↔ rendu.
 * Aucune règle de jeu ici : elles vivent dans core/ et game/, testées à part.
 */
import { mulberry32, dayKey } from './core/rng.js';
import { levelSpec, dailySpec, chapterOf, LEVELS_PER_CHAPTER, ROCKS_FROM_LEVEL } from './core/levels.js';
import { starsFor, streakAfter, hasShield, totalStars, rankFor } from './core/rules.js';
import { shouldShowInterstitial, hintsForWin, dailyRotation, eventWindow, HALLOWEEN, NO_ADS_PRICE_EUR, CHAPTER_REWARD_HINTS, formatEur } from './core/economy.js';
import { loadSave, writeSave, memoryStorage } from './core/storage.js';
import { createAnalytics } from './core/analytics.js';
import { createSession, tap, step, freeCreatures, reviveWithHeart } from './game/session.js';
import { createBackground } from './render/background.js';
import { createParticles, SHAPE } from './render/particles.js';
import { createBoardRenderer } from './render/board.js';
import { drawCreature, createSpriteCache } from './render/sprites.js';
import { hexToRgb } from './render/gl.js';
import { createSfx } from './audio/sfx.js';
import { THEMES, themeOf } from './config/themes.js';
import { TEXTS } from './config/texts.fr.js';
import { createLocalLeaderboard } from './services/leaderboard.js';
import { $, $$, esc, openModal, closeModal, toast, showAd, copyText } from './ui/dom.js';

const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const TAU = Math.PI * 2;
const pick = a => a[Math.floor(Math.random() * a.length)];
const fmtTime = s => { s = Math.floor(s); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
const fmtLeft = ms => {
  const s = Math.max(0, Math.floor(ms / 1000)), d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60), x = s % 60, p = n => String(n).padStart(2, '0');
  return d ? `${d} j ${h} h ${p(m)} min` : `${p(h)}:${p(m)}:${p(x)}`;
};

/* ---------- Services ---------- */
const storage = (() => { try { const t = '__td'; localStorage.setItem(t, '1'); localStorage.removeItem(t); return localStorage; } catch (e) { return memoryStorage(); } })();
const save = loadSave(storage);
const persist = () => writeSave(storage, save);
const analytics = createAnalytics({ storage, sink: location.hash === '#debug' ? e => console.debug('[analytics]', e) : null });
const leaderboard = createLocalLeaderboard(() => save, persist);
const sfx = createSfx(() => save.muted);
const buzz = p => { if (!save.haptics) return; try { navigator.vibrate && navigator.vibrate(p); } catch (e) { /* non supporté */ } };
const theme = () => themeOf(save.theme);

/* ---------- Rendu ---------- */
const bg = createBackground($('#bg'));
const fx = createParticles($('#fx'), { max: RM ? 400 : 2400 });
const board = createBoardRenderer($('#cv'), { reducedMotion: RM });
const heroSprites = createSpriteCache();

/* ---------- État de l'application ---------- */
let screen = 'home', s = null, T = 0, shake = 0, floats = [], hint = null, hintT = 0, startedAt = 0, tipTimer = 0;

function startGame(mode) {
  const daily = mode === 'daily';
  const spec = daily ? dailySpec(dayKey()) : levelSpec(save.level);
  s = createSession({ spec, mode, shield: !daily && hasShield(save.streak) });
  floats = []; hint = null; hintT = 0; startedAt = T; fx.clear();
  show('game');
  if (daily) {
    $('#gTitle').textContent = 'Défi du ' + new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
    $('#gSub').textContent = 'Même grille pour tout le monde';
  } else {
    const ch = chapterOf(save.level);
    $('#gTitle').textContent = 'Niveau ' + save.level;
    $('#gSub').textContent = `Chapitre ${ch.number} · ${ch.name}`;
  }
  $('#badgeHard').hidden = !spec.hard || daily;
  board.layout(s.rows, s.cols);
  hud();
  analytics.track('level_start', { mode, level: spec.level, rows: spec.rows, cols: spec.cols, creatures: s.total });

  if (!daily && save.level === 1) { hint = freeCreatures(s)[0] || null; hintT = 999; tip('first'); }
  else if (!daily && save.level === ROCKS_FROM_LEVEL) tip('rocks');
  else if (s.shield) tip('shield');
  else if (spec.hard && !daily) tip('hard');
}

function tip(id, force = false) {
  if (!force && save.seenTips.includes(id) && id !== 'shield' && id !== 'hard') return;
  if (!save.seenTips.includes(id)) { save.seenTips.push(id); persist(); }
  const el = $('#tip'); el.textContent = TEXTS.tips[id]; el.hidden = false;
  clearTimeout(tipTimer); tipTimer = setTimeout(() => { el.hidden = true; }, 5000);
}

function hud() {
  if (!s) return;
  $('#gLeft').textContent = `${s.left} / ${s.total}`;
  $$('#hearts i').forEach((h, i) => h.classList.toggle('off', i >= s.hearts));
  $('#gTimer').textContent = '⏱ ' + fmtTime(s.time);
  $('#badgeShield').hidden = !s.shield;
  const hb = $('#hintBtn');
  hb.textContent = `💡 Indice ×${save.hints}`;
  hb.disabled = save.hints <= 0 || s.over;
}

/* ---------- Entrées ---------- */
$('#cv').addEventListener('pointerdown', e => {
  sfx.unlock();
  if (!s || s.over) return;
  const { r, c } = board.cellAt(e.clientX, e.clientY);
  const evs = tap(s, r, c, T);
  if (evs.length) { $('#tip').hidden = true; if (hint && hintT > 100) { hint = null; hintT = 0; } }
  handle(evs);
});

/* ---------- Événements de la session → sons, particules, interface ---------- */
function burst(x, y, n, speed, color, opts = {}) {
  for (let i = 0; i < (RM ? Math.ceil(n / 4) : n); i++) {
    const an = Math.random() * TAU, sp = speed * (0.4 + Math.random() * 0.6);
    fx.emit(x, y, Math.cos(an) * sp + (opts.vx || 0), Math.sin(an) * sp + (opts.vy || 0), opts.life || 0.6, opts.size ? opts.size * (0.6 + Math.random() * 0.6) : 4 + Math.random() * 6,
      i % 3 || opts.mono ? color : [1, 1, 1], 1, opts.shape ?? SHAPE.bead, opts.grav || 0, opts.drag ?? 3.5);
  }
}

function handle(evs) {
  const th = theme(), { cs } = board.view;
  for (const ev of evs) {
    const k = ev.k;
    switch (ev.type) {
      case 'exit':
        sfx.whoosh(ev.combo); buzz(8);
        if (hint === k) hint = null;
        if (Math.random() < 0.28) floats.push({ x: board.kx(k), y: board.ky(k) - cs * 0.55, text: pick(TEXTS.exit), col: '#fff', size: Math.max(14, cs * 0.32), life: 1 });
        if (ev.combo >= 3) {
          const text = th.mask && Math.random() < 0.4 ? pick(TEXTS.messageA) : pick(TEXTS.combo).replace('{n}', ev.combo);
          floats.push({ x: board.view.W / 2, y: Math.max(30, board.view.by - 10), text, col: '#ffd23f', size: 22, life: 1.4, big: true });
          bg.pulse(0.35);
        }
        break;
      case 'bump': sfx.tap(); break;
      case 'rock':
        sfx.rock(); buzz(5);
        floats.push({ x: board.view.bx + (ev.rock.c + 0.5) * cs, y: board.view.by + (ev.rock.r + 0.1) * cs, text: pick(TEXTS.rock), col: '#cbd5e1', size: 15, life: 0.8 });
        break;
      case 'cross': {
        const [x, y] = board.toViewport(board.kx(k), board.ky(k)), [dr, dc] = [[-1, 0], [0, 1], [1, 0], [0, -1]][k.dir];
        burst(x, y, 14, 280, hexToRgb(th.dirs[k.dir]), { vx: dc * 160, vy: dr * 160 });
        break;
      }
      case 'impact': {
        const [dr, dc] = [[-1, 0], [0, 1], [1, 0], [0, -1]][k.dir];
        const [x, y] = board.toViewport(board.kx(k) + dc * cs * 0.45, board.ky(k) + dr * cs * 0.45);
        if (ev.shielded) {
          sfx.shield(); buzz(15);
          burst(x, y, 16, 220, [0.5, 0.9, 1], { mono: true, shape: SHAPE.glow, size: 18, life: 0.5 });
          floats.push({ x: board.kx(k), y: board.ky(k) - cs * 0.6, text: TEXTS.shield, col: '#7dd3fc', size: 18, life: 1.2 });
        } else {
          sfx.bonk(); buzz([25, 30, 25]); if (!RM) shake = 7;
          burst(x, y, 10, 200, [1, 0.85, 0.25], { mono: true, grav: 420, vy: -60, life: 0.5, drag: 1.5 });
          floats.push({ x: board.kx(k), y: board.ky(k) - cs * 0.6, text: pick(TEXTS.bump), col: '#fff', size: Math.max(14, cs * 0.32), life: 1 });
          const hi = $$('#hearts i')[s.hearts];
          if (hi) { hi.classList.remove('pop'); void hi.offsetWidth; hi.classList.add('pop'); }
        }
        break;
      }
      case 'win': setTimeout(winGame, 650); break;
      case 'lose': setTimeout(loseGame, 750); break;
    }
  }
  if (evs.length) hud();
}

/* ---------- Boucle principale ---------- */
let last = performance.now(), frameN = 0;
function frame(now) {
  const dt = Math.min(0.033, (now - last) / 1000); last = now; T += dt; frameN++;
  if (screen === 'game' && s) {
    const before = Math.floor(s.time);
    handle(step(s, dt));
    if (Math.floor(s.time) !== before) $('#gTimer').textContent = '⏱ ' + fmtTime(s.time);
    if (hintT > 0) { hintT -= dt; if (hintT <= 0) hint = null; }
    if (!RM) {
      const th = theme(), { cs } = board.view;
      for (const k of s.list) {
        if (k.st !== 'exit') continue;
        const [dr, dc] = [[-1, 0], [0, 1], [1, 0], [0, -1]][k.dir], [x, y] = board.toViewport(board.kx(k), board.ky(k));
        for (let i = 0; i < 2; i++) fx.emit(x - dc * cs * 0.3 + (Math.random() - 0.5) * cs * 0.2, y - dr * cs * 0.3 + (Math.random() - 0.5) * cs * 0.2, -dc * 20, -dr * 20, 0.32, cs * (0.55 + Math.random() * 0.2), hexToRgb(th.dirs[k.dir]), 0.45, SHAPE.glow, 0, 2, -cs * 0.8);
      }
    }
    for (const f of floats) { f.y -= (f.big ? 18 : 40) * dt; f.life -= dt * (f.big ? 0.7 : 1.1); }
    if (floats.length) floats = floats.filter(f => f.life > 0);
    shake = Math.max(0, shake - dt * 40);
    board.draw(s, theme(), T, { floats, hint, shake, age: T - startedAt });
  } else if (screen === 'home') drawHero(dt);
  fx.update(dt); fx.render();
  if (frameN % 2 === 0) bg.render(T, dt * 2);
  requestAnimationFrame(frame);
}

/* ---------- Accueil ---------- */
const hero = $('#heroCv'), hctx = hero.getContext('2d');
let hW = 300;
const heroK = [0, 1, 2, 3, 1].map((dir, i) => ({ dir, seed: i * 1.7, expr: 0, blink: 1 + i }));
function sizeHero() {
  const d = Math.min(devicePixelRatio || 1, 2);
  hW = hero.clientWidth || 300;
  hero.width = Math.round(hW * d); hero.height = Math.round(120 * d);
  hctx.setTransform(d, 0, 0, d, 0, 0); heroSprites.clear();
}
function drawHero(dt) {
  const th = theme(), d = Math.min(devicePixelRatio || 1, 2), sz = Math.min(64, hW / 6.2), n = heroK.length;
  hctx.clearRect(0, 0, hW, 120);
  heroK.forEach((k, i) => {
    k.blink -= dt; if (k.blink < 0) { k.expr = k.expr ? 0 : 1; k.blink = k.expr ? 0.12 : 2 + Math.random() * 4; }
    const spr = heroSprites.creature(th, k.dir, k.expr, Math.round(sz * d)), S = spr.width / d;
    const x = hW / 2 + (i - (n - 1) / 2) * sz * 1.15, y = 66 + (RM ? 0 : Math.sin(T * 2.2 + k.seed) * 5);
    hctx.drawImage(spr, x - S / 2, y - S / 2, S, S);
  });
}
function renderHome() {
  const ch = chapterOf(save.level), stars = totalStars(save.stars), rank = rankFor(stars);
  $('#playBtn').textContent = 'Jouer · Niveau ' + save.level;
  $('#rankName').textContent = rank.name;
  $('#rankStars').textContent = `${stars} ★`;
  $('#rankNext').textContent = rank.next ? `Prochain rang à ${rank.next.stars} ★ : ${rank.next.name}` : 'Rang maximum atteint';
  $('#rankBar').style.width = rank.next ? `${Math.min(100, (stars / rank.next.stars) * 100)}%` : '100%';
  $('#streak').textContent = save.streak >= 1 ? `🔥 Série : ${save.streak}` : '🔥 Série : 0';
  $('#chapterName').textContent = `Chapitre ${ch.number} · ${ch.name}`;
  $('#chapterPips').innerHTML = Array.from({ length: LEVELS_PER_CHAPTER }, (_, i) => `<i class="${i + 1 < ch.position ? 'done' : i + 1 === ch.position ? 'cur' : ''}"></i>`).join('');
  const best = leaderboard.best(dayKey());
  $('#dailyInfo').textContent = best ? 'Ton temps : ' + fmtTime(best) : 'Même grille pour tout le monde';
  $('#soundBtn').textContent = save.muted ? '🔇 Son coupé' : '🔊 Son';
  $('#hapticBtn').textContent = save.haptics ? '📳 Vibrations' : '📴 Vibrations coupées';
  requestAnimationFrame(sizeHero);
}

/* ---------- Navigation ---------- */
const SCREENS = { home: '#scrHome', game: '#scrGame', shop: '#scrShop' };
function show(name) {
  screen = name;
  for (const k in SCREENS) $(SCREENS[k]).hidden = k !== name;
  if (name !== 'game') { s = null; fx.clear(); $('#tip').hidden = true; }
  if (name === 'home') renderHome();
  if (name === 'shop') renderShop();
}
document.addEventListener('click', e => {
  const b = e.target.closest('[data-go]'); if (!b) return;
  sfx.unlock();
  if (b.dataset.go === 'daily') startGame('daily'); else show(b.dataset.go);
});
$('#playBtn').onclick = () => { sfx.unlock(); startGame('level'); };
$('#backBtn').onclick = () => { if (s && s.started && !s.over) analytics.track('level_quit', { level: s.spec.level, left: s.left }); show('home'); };
$('#restartBtn').onclick = () => { if (s) startGame(s.mode); };
$('#soundBtn').onclick = () => { save.muted = !save.muted; persist(); renderHome(); };
$('#hapticBtn').onclick = () => { save.haptics = !save.haptics; persist(); renderHome(); buzz(20); };
$('#hintBtn').onclick = () => {
  if (!s || s.over || save.hints <= 0) return;
  const free = freeCreatures(s);
  if (!free.length) return;
  save.hints--; persist();
  hint = pick(free); hintT = 3; sfx.hint(); hud();
  analytics.track('hint_used', { level: s.spec.level });
};

/* ---------- Fin de niveau ---------- */
function celebrate() {
  bg.pulse(1);
  const th = theme(), r = board.view.rect;
  for (let i = 0; i < (RM ? 40 : 220); i++) {
    fx.emit(Math.random() * innerWidth, -20 - Math.random() * 200, (Math.random() - 0.5) * 140, 120 + Math.random() * 260, 2.2 + Math.random() * 1.4, 9 + Math.random() * 9, i % 5 ? hexToRgb(th.dirs[i % 4]) : [1, 1, 1], 1, SHAPE.confetti, 160, 0.6);
  }
  burst(r.left + board.view.W / 2, r.top + board.view.H / 2, 60, 620, hexToRgb(th.dirs[0]), { shape: SHAPE.glow, size: 20, life: 1, drag: 2.2 });
}
const starsHtml = n => `<div class="stars" aria-label="${n} étoiles sur 3">${'★'.repeat(n)}<span>${'★'.repeat(3 - n)}</span></div>`;

function winGame() {
  if (!s) return;
  const g = s, st = starsFor(g.mistakes);
  sfx.win(); buzz([20, 40, 20, 40, 60]); celebrate();
  analytics.track(g.mode === 'daily' ? 'daily_win' : 'level_win', { level: g.spec.level, seconds: Math.round(g.time), mistakes: g.mistakes, stars: st });

  if (g.mode === 'daily') {
    const k = dayKey(), res = leaderboard.submit(k, Math.max(0.1, g.time));
    let reward = '';
    if (!save.dailyRewarded[k]) { save.dailyRewarded[k] = true; save.hints++; reward = '<p><b>+1 💡 indice gagné (1 par jour)</b></p>'; }
    persist();
    const d = new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
    const txt = `Tous Dehors · Défi du ${d}\n⏱ ${fmtTime(g.time)} · ${g.mistakes} bouchon${g.mistakes > 1 ? 's' : ''}\n${'🟩'.repeat(st)}${'⬛'.repeat(3 - st)}`;
    const hist = leaderboard.history(5).map(h => `<li><span>${String(h.day).slice(6)}/${String(h.day).slice(4, 6)}</span><b>${fmtTime(h.seconds)}</b></li>`).join('');
    openModal(`<h3>${res.record ? 'Nouveau record !' : 'Défi réussi'}</h3>${starsHtml(st)}<div class="big">⏱ ${fmtTime(g.time)}</div>
      <p>${esc(pick(TEXTS.win))}</p>${reward}
      <ol class="hist" aria-label="Tes derniers défis">${hist}</ol>
      <textarea id="shareTxt" rows="3" readonly aria-label="Ton résultat à partager">${esc(txt)}</textarea>
      <button class="btn gold" data-act="copy">Copier mon résultat</button>
      <div class="row"><button class="btn" data-act="home">Accueil</button><button class="btn alt" data-act="retry">Rejouer</button></div>`,
    async act => {
      if (act === 'copy') { const ok = await copyText(txt, $('#shareTxt')); toast(ok ? 'Copié ! Colle-le dans ta conversation.' : 'Sélectionné : copie-le à la main.'); analytics.track('share', { kind: 'daily' }); return; }
      closeModal(); if (act === 'retry') startGame('daily'); else show('home');
    });
    return;
  }

  const L = save.level, ch = chapterOf(L);
  save.stars[L] = Math.max(save.stars[L] || 0, st);
  save.level++; save.wins++; save.streak = streakAfter(save.streak, true);
  let reward = '';
  if (hintsForWin(save.wins)) { save.hints++; reward += '<p><b>+1 💡 indice gagné</b></p>'; }
  const chapterDone = L === ch.last;
  if (chapterDone) { save.hints += CHAPTER_REWARD_HINTS; reward += `<p><b>Chapitre « ${esc(ch.name)} » terminé ! +${CHAPTER_REWARD_HINTS} 💡</b></p>`; }
  persist();
  const streakTxt = save.streak >= 2 ? `<p class="streakline">🔥 Série de ${save.streak} victoires${hasShield(save.streak) ? ' · 🛡️ bouclier actif' : ''}</p>` : '';
  openModal(`<h3>${chapterDone ? 'Chapitre terminé !' : `Niveau ${L} réussi`}</h3>${starsHtml(st)}<p>${esc(pick(TEXTS.win))}</p>
    <p class="fine">⏱ ${fmtTime(g.time)} · ${g.mistakes} bouchon${g.mistakes > 1 ? 's' : ''}</p>${streakTxt}${reward}
    <div class="row"><button class="btn" data-act="next">Niveau ${L + 1}</button><button class="btn alt" data-act="home">Accueil</button></div>`,
  act => {
    closeModal();
    const go = () => (act === 'next' ? startGame('level') : show('home'));
    if (shouldShowInterstitial({ level: L, wins: save.wins, noAds: save.noAds })) {
      analytics.track('ad_interstitial', { level: L });
      showAd({ ad: pick(TEXTS.ads), onDone: go });
    } else go();
  });
}

function loseGame() {
  if (!s) return;
  const g = s;
  sfx.sad();
  if (g.mode === 'level') { save.streak = streakAfter(save.streak, false); persist(); }
  analytics.track(g.mode === 'daily' ? 'daily_fail' : 'level_fail', { level: g.spec.level, left: g.left, seconds: Math.round(g.time) });
  openModal(`<h3>Plus de cœurs</h3><div class="big">😵</div><p>${esc(pick(TEXTS.lose))}</p>
    <p class="fine">Encore ${g.left} bestiole${g.left > 1 ? 's' : ''} à libérer.</p>
    ${g.revived ? '' : '<button class="btn gold" data-act="ad">📺 +1 cœur en regardant une pub</button>'}
    <div class="row"><button class="btn" data-act="retry">Recommencer</button><button class="btn alt" data-act="home">Accueil</button></div>`,
  act => {
    closeModal();
    if (act === 'ad') {
      analytics.track('ad_rewarded', { level: g.spec.level });
      showAd({ reward: '+1 cœur', ad: pick(TEXTS.ads), onDone: () => { if (s === g && reviveWithHeart(g)) { g.revived = true; hud(); toast('+1 cœur. Fais-en bon usage.'); } } });
    } else if (act === 'retry') startGame(g.mode);
    else show('home');
  });
}

/* ---------- Boutique ---------- */
function shopCard(id, chip) {
  const t = THEMES[id], own = save.owned.includes(id), on = save.theme === id;
  const btn = own
    ? `<button class="btn ${on ? 'alt' : 'gold'} small" data-equip="${id}" ${on ? 'disabled' : ''}>${on ? 'Équipé' : 'Équiper'}</button>`
    : `<button class="btn small" data-buy="${id}">${formatEur(t.price)}</button>`;
  return `<div class="card">${chip ? `<span class="chip">${chip}</span>` : ''}<canvas data-prev="${id}" width="288" height="120"></canvas><b>${esc(t.name)}</b><p>${esc(t.desc)}</p>${btn}</div>`;
}
function renderShop() {
  const ev = eventWindow(new Date(), HALLOWEEN);
  $('#shopEvent').innerHTML = ev.active ? shopCard('halloween', 'ÉVÉNEMENT · ' + fmtLeft(ev.end - new Date())) : '';
  $('#shopDaily').innerHTML = dailyRotation(THEMES, mulberry32(dayKey() * 7 + 3)).map(id => shopCard(id, '')).join('');
  $('#shopOther').innerHTML = `<div class="card"><b>Sans pub imposée</b><p>Retire toutes les pubs imposées pour toujours. Les pubs « +1 cœur » restent au choix.</p>${save.noAds ? '<button class="btn alt small" disabled>Activé</button>' : `<button class="btn small" data-buy="noads">${formatEur(NO_ADS_PRICE_EUR)}</button>`}</div>
    <div class="card ghost"><span class="chip">BIENTÔT</span><b>Skin créateur</b><p>Les bestioles aux couleurs de ton créateur TikTok préféré. Une partie du prix lui revient.</p><button class="btn alt small" disabled>Collab en préparation</button></div>`;
  $('#shopOwned').innerHTML = save.owned.filter(id => THEMES[id]).map(id => `<button data-equip="${id}" class="${save.theme === id ? 'on' : ''}">${esc(THEMES[id].name)}</button>`).join('');
  $$('canvas[data-prev]').forEach(cnv => {
    const th = THEMES[cnv.dataset.prev], c = cnv.getContext('2d'), g = c.createLinearGradient(0, 0, 0, cnv.height);
    g.addColorStop(0, th.bg[1]); g.addColorStop(1, th.bg[0]); c.fillStyle = g; c.fillRect(0, 0, cnv.width, cnv.height);
    [0, 1, 2, 3].forEach(d => { c.save(); c.translate(36 + d * 72, 62); drawCreature(c, 62, th, d, d === 2 ? 3 : 0); c.restore(); });
  });
  tick();
}
function applyTheme() {
  const th = theme(); board.sprites.clear(); heroSprites.clear(); bg.setTheme(th);
  const r = document.documentElement.style;
  r.setProperty('--accent', th.dirs[0]); r.setProperty('--accent2', th.dirs[1]); r.setProperty('--bg', th.bg[0]);
}
$('#scrShop').addEventListener('click', e => {
  const eq = e.target.closest('[data-equip]');
  if (eq) { save.theme = eq.dataset.equip; persist(); applyTheme(); sfx.tap(); toast('Skin équipé : ' + theme().name); renderShop(); return; }
  const bu = e.target.closest('[data-buy]'); if (!bu) return;
  const id = bu.dataset.buy, isAds = id === 'noads', name = isAds ? 'Sans pub imposée' : THEMES[id].name, price = isAds ? NO_ADS_PRICE_EUR : THEMES[id].price;
  openModal(`<h3>Confirmer l’achat</h3><p>Acheter <b>${esc(name)}</b> pour <b>${formatEur(price)}</b> ?</p>
    <p class="fine">${isAds ? '' : 'Skin uniquement cosmétique, sans avantage en jeu. '}Prototype : aucun paiement réel. Dans l’appli, le paiement passe par Google Play.</p>
    <div class="row"><button class="btn" data-act="buy">Acheter ${formatEur(price)}</button><button class="btn alt" data-act="cancel">Annuler</button></div>`,
  act => {
    closeModal(); if (act !== 'buy') return;
    if (isAds) { save.noAds = true; toast('Pubs imposées retirées.'); }
    else { if (!save.owned.includes(id)) save.owned.push(id); save.theme = id; applyTheme(); toast(name + ' débloqué et équipé.'); }
    persist(); sfx.cash(); renderShop();
    analytics.track('purchase_simulated', { item: id, price });
  });
});

let shopDay = dayKey();
function tick() {
  const now = new Date(), mid = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1), left = fmtLeft(mid - now);
  $('#shopTimer').textContent = left; $('#homeShopTimer').textContent = left;
  const ev = eventWindow(now, HALLOWEEN);
  $('#homeEvent').hidden = !ev.active;
  if (ev.active) {
    $('#homeEventLeft').textContent = fmtLeft(ev.end - now);
    const chip = document.querySelector('#shopEvent .chip'); if (chip) chip.textContent = 'ÉVÉNEMENT · ' + fmtLeft(ev.end - now);
  }
  if (screen === 'shop' && shopDay !== dayKey()) { shopDay = dayKey(); renderShop(); }
}

/* ---------- Démarrage ---------- */
function onResize() { bg.resize(); fx.resize(); sizeHero(); if (screen === 'game' && s) board.layout(s.rows, s.cols); }
addEventListener('resize', onResize);
applyTheme(); bg.resize(); fx.resize(); renderHome(); tick();
setInterval(tick, 1000);
analytics.track('app_open', { level: save.level, streak: save.streak });
requestAnimationFrame(frame);

if (location.hash === '#debug') {
  window.__td = {
    free: () => (s ? freeCreatures(s).map(k => board.toViewport(board.kx(k), board.ky(k))) : []),
    state: () => s && { left: s.left, hearts: s.hearts, over: s.over, result: s.result },
    events: () => analytics.events(),
  };
}

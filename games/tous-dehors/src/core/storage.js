/**
 * Sauvegarde locale validée.
 * Toute donnée relue est filtrée champ par champ : une sauvegarde corrompue
 * ou modifiée à la main retombe sur des valeurs sûres au lieu de casser le jeu.
 */
export const SAVE_KEY = 'tous-dehors-v2';
export const LEGACY_KEYS = Object.freeze(['tous-dehors-v1']);
const ID = /^[a-zA-Z][a-zA-Z0-9]{0,31}$/;

export function defaultSave() {
  return {
    v: 2, level: 1, hints: 3, streak: 0, wins: 0, stars: {}, owned: ['pastel'], theme: 'pastel',
    noAds: false, daily: {}, dailyRewarded: {}, muted: false, haptics: true, seenTips: [],
  };
}

const int = (v, min, max, def) => (Number.isInteger(v) && v >= min && v <= max ? v : def);
const bool = (v, def) => (typeof v === 'boolean' ? v : def);

export function sanitize(raw) {
  const d = defaultSave();
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return d;
  const out = { ...d };
  out.level = int(raw.level, 1, 100000, d.level);
  out.hints = int(raw.hints, 0, 999, d.hints);
  out.streak = int(raw.streak, 0, 100000, d.streak);
  out.wins = int(raw.wins ?? raw.done, 0, 1000000, d.wins);
  out.noAds = bool(raw.noAds, d.noAds);
  out.muted = bool(raw.muted, d.muted);
  out.haptics = bool(raw.haptics, d.haptics);
  out.stars = {};
  if (raw.stars && typeof raw.stars === 'object') {
    for (const [k, v] of Object.entries(raw.stars)) if (/^\d{1,6}$/.test(k) && int(v, 1, 3, 0)) out.stars[k] = v;
  }
  out.daily = {};
  if (raw.daily && typeof raw.daily === 'object') {
    for (const [k, v] of Object.entries(raw.daily)) if (/^\d{8}$/.test(k) && typeof v === 'number' && v > 0 && v < 86400) out.daily[k] = v;
  }
  out.dailyRewarded = {};
  if (raw.dailyRewarded && typeof raw.dailyRewarded === 'object') {
    for (const k of Object.keys(raw.dailyRewarded)) if (/^\d{8}$/.test(k)) out.dailyRewarded[k] = true;
  }
  const owned = Array.isArray(raw.owned) ? raw.owned.filter(x => typeof x === 'string' && ID.test(x)) : [];
  out.owned = Array.from(new Set(['pastel', ...owned]));
  out.theme = typeof raw.theme === 'string' && out.owned.includes(raw.theme) ? raw.theme : 'pastel';
  out.seenTips = Array.isArray(raw.seenTips) ? raw.seenTips.filter(x => typeof x === 'string' && ID.test(x)).slice(0, 50) : [];
  return out;
}

/** storage : objet compatible localStorage (injecté pour les tests). */
export function loadSave(storage) {
  try {
    const cur = storage.getItem(SAVE_KEY);
    if (cur) return sanitize(JSON.parse(cur));
    for (const k of LEGACY_KEYS) {
      const old = storage.getItem(k);
      if (old) return sanitize(JSON.parse(old));
    }
  } catch (e) { /* stockage bloqué ou JSON corrompu : on repart des valeurs par défaut */ }
  return defaultSave();
}

export function writeSave(storage, data) {
  try { storage.setItem(SAVE_KEY, JSON.stringify(sanitize(data))); return true; } catch (e) { return false; }
}

/** Stockage en mémoire, utilisé quand localStorage est indisponible et dans les tests. */
export function memoryStorage() {
  const m = new Map();
  return {
    getItem: k => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { m.set(k, String(v)); },
    removeItem: k => { m.delete(k); },
  };
}

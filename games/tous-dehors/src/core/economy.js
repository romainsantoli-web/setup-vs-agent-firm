/**
 * Économie et règles de monétisation. Tout ce qui touche à l'argent ou aux pubs
 * passe par ici, pour que les règles promises aux joueurs soient testées.
 *
 * Règles de la maison :
 * - indices gagnés en jouant, jamais vendus ;
 * - pubs récompensées toujours au choix ;
 * - au plus une pub imposée tous les 3 niveaux, aucune avant le niveau 11 ;
 * - skins 100 % cosmétiques, prix en euros, sans monnaie virtuelle.
 */
export const AD_RULES = Object.freeze({ firstInterstitialLevel: 11, everyNWins: 3 });
export const NO_ADS_PRICE_EUR = 2.99;
export const HINT_EVERY_N_WINS = 3;
export const CHAPTER_REWARD_HINTS = 2;

export function shouldShowInterstitial({ level, wins, noAds }) {
  if (!Number.isInteger(level) || level < 1) throw new RangeError(`niveau invalide : ${level}`);
  if (!Number.isInteger(wins) || wins < 0) throw new RangeError(`victoires invalides : ${wins}`);
  if (noAds) return false;
  return level >= AD_RULES.firstInterstitialLevel && wins > 0 && wins % AD_RULES.everyNWins === 0;
}

export function hintsForWin(wins) {
  if (!Number.isInteger(wins) || wins < 1) throw new RangeError(`victoires invalides : ${wins}`);
  return wins % HINT_EVERY_N_WINS === 0 ? 1 : 0;
}

/** Boutique du jour : sélection déterministe de skins payants hors événement. */
export function dailyRotation(themes, rnd, count = 3) {
  const pool = Object.keys(themes).filter(id => themes[id].price > 0 && !themes[id].event);
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, Math.max(0, count));
}

/** Fenêtre d'un événement saisonnier [début, fin] dans l'année courante. */
export function eventWindow(now, { month, startDay, endDay }) {
  const y = now.getFullYear();
  const start = new Date(y, month, startDay, 0, 0, 0);
  const end = new Date(y, month, endDay, 23, 59, 59);
  return { active: now >= start && now <= end, start, end };
}

export const HALLOWEEN = Object.freeze({ month: 9, startDay: 1, endDay: 31 });

export function formatEur(n) {
  return n.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' });
}

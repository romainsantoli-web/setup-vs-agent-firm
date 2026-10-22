/**
 * Classement du défi du jour, derrière une interface remplaçable.
 * Version actuelle : locale (meilleurs temps du joueur sur ses derniers jours).
 * Pour un vrai classement mondial, brancher un adaptateur Google Play Games Services
 * ou un backend (Firebase) qui implémente les mêmes méthodes submit() et history().
 */
export function createLocalLeaderboard(getSave, persist) {
  return {
    kind: 'local',
    submit(dayKey, seconds) {
      if (!Number.isInteger(dayKey) || !(seconds > 0 && seconds < 86400)) throw new RangeError('résultat invalide');
      const s = getSave(), prev = s.daily[dayKey];
      const record = !prev || seconds < prev;
      if (record) { s.daily[dayKey] = Math.round(seconds * 10) / 10; persist(); }
      return { record, best: s.daily[dayKey] };
    },
    best(dayKey) { return getSave().daily[dayKey] || null; },
    history(limit = 7) {
      return Object.entries(getSave().daily).sort((a, b) => b[0] - a[0]).slice(0, limit).map(([k, v]) => ({ day: +k, seconds: v }));
    },
  };
}

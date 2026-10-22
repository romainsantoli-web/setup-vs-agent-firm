/**
 * Analytics minimal et remplaçable.
 * Les éditeurs (Voodoo, Homa…) jugent un prototype sur la rétention et l'entonnoir
 * de niveaux : on journalise dès maintenant les événements clés. Le « sink » permet
 * de brancher plus tard Firebase ou un autre outil sans toucher au jeu.
 */
const NAME = /^[a-z][a-z0-9_]{1,39}$/;

export function createAnalytics({ storage, key = 'tous-dehors-events', max = 300, sink = null, now = () => Date.now() } = {}) {
  let buffer = [];
  try { const raw = storage && storage.getItem(key); if (raw) buffer = JSON.parse(raw).slice(-max); } catch (e) { buffer = []; }
  const flush = () => { try { storage && storage.setItem(key, JSON.stringify(buffer)); } catch (e) { /* quota plein : on garde en mémoire */ } };

  function track(name, props = {}) {
    if (!NAME.test(name)) throw new RangeError(`nom d'événement invalide : ${name}`);
    const clean = {};
    for (const [k, v] of Object.entries(props)) {
      if (['string', 'number', 'boolean'].includes(typeof v)) clean[k] = typeof v === 'string' ? v.slice(0, 64) : v;
    }
    const ev = { name, t: now(), ...clean };
    buffer.push(ev);
    if (buffer.length > max) buffer = buffer.slice(-max);
    flush();
    if (sink) { try { sink(ev); } catch (e) { /* un outil externe en panne ne doit jamais casser le jeu */ } }
    return ev;
  }
  return { track, events: () => buffer.slice(), clear: () => { buffer = []; flush(); } };
}

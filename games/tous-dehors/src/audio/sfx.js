/**
 * Effets sonores synthétisés en WebAudio : aucun fichier audio à charger.
 * Le contexte audio ne démarre qu'après un geste du joueur (règle des navigateurs).
 */
export function createSfx(isMuted) {
  let ac = null;
  const audio = () => {
    if (isMuted()) return null;
    if (!ac) { try { ac = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { return null; } }
    if (ac.state === 'suspended') ac.resume();
    return ac;
  };

  function tone(f1, f2, dur, type = 'sine', vol = 0.14, delay = 0) {
    const c = audio(); if (!c) return;
    const t = c.currentTime + delay, o = c.createOscillator(), g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(f1, t); o.frequency.exponentialRampToValueAtTime(f2, t + dur);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(c.destination); o.start(t); o.stop(t + dur + 0.02);
  }

  function sweep(dur, f1, f2, vol) {
    const c = audio(); if (!c) return;
    const t = c.currentTime;
    const b = c.createBuffer(1, Math.floor(c.sampleRate * dur), c.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
    s.buffer = b; f.type = 'bandpass'; f.Q.value = 1.4;
    f.frequency.setValueAtTime(f1, t); f.frequency.exponentialRampToValueAtTime(f2, t + dur);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + dur * 0.25); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    s.connect(f); f.connect(g); g.connect(c.destination); s.start(t);
  }

  return {
    unlock: () => audio(),
    whoosh(combo) {
      sweep(0.26, 500, 3800, 0.22);
      const f = 520 * Math.pow(1.0595, Math.min(combo - 1, 14) * 2);
      tone(f, f * 1.5, 0.14, 'triangle', 0.1);
    },
    tap: () => tone(700, 520, 0.06, 'triangle', 0.08),
    rock: () => tone(260, 180, 0.08, 'square', 0.05),
    bonk() { tone(220, 70, 0.22, 'sine', 0.3); tone(1400, 900, 0.05, 'square', 0.04); },
    shield() { tone(660, 1320, 0.2, 'triangle', 0.12); tone(990, 1980, 0.2, 'sine', 0.06, 0.05); },
    win: () => [523, 659, 784, 1046, 1318].forEach((f, i) => tone(f, f * 1.01, 0.22, 'triangle', 0.11, i * 0.09)),
    sad: () => [440, 370, 294].forEach((f, i) => tone(f, f * 0.97, 0.32, 'triangle', 0.12, i * 0.2)),
    cash() { tone(880, 1320, 0.1, 'triangle', 0.12); tone(1320, 1760, 0.16, 'triangle', 0.12, 0.09); },
    hint: () => tone(988, 1480, 0.18, 'sine', 0.1),
  };
}

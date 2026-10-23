/**
 * Skins : uniquement cosmétiques. dirs = couleur par direction (haut, droite, bas, gauche),
 * bg = 4 couleurs du fond WebGL. Ajouter un skin = ajouter une entrée ici.
 */
export const THEMES = Object.freeze({
  pastel: { name: 'Pastel', price: 0, dirs: ['#ff6b8b', '#ffb547', '#4fd1a5', '#5aa9ff'], bg: ['#2b48c8', '#6cb8ff', '#ffffff', '#ffd36b'], desc: 'Les bestioles d’origine. Douces, mais pressées.' },
  halloween: { name: 'Citrouilles Maudites', price: 1.99, event: true, dirs: ['#ff7a1a', '#a78bfa', '#84cc16', '#f43f5e'], bg: ['#0f0a14', '#2a1036', '#ff7a1a', '#a78bfa'], stem: true, desc: 'Édition Halloween. Disparaît le 31 octobre à minuit.' },
  neon: { name: 'Néon Nuit', price: 1.49, dirs: ['#ff2bd6', '#ffe600', '#00ffa3', '#00b3ff'], bg: ['#05040f', '#1a0b3d', '#00e5ff', '#ff2bd6'], desc: 'Ça brille. Ça file. Ça clignote un peu.' },
  givre: { name: 'Givre', price: 0.99, dirs: ['#7dd3fc', '#a5b4fc', '#5eead4', '#f0abfc'], bg: ['#1f5f9e', '#8fd3ff', '#ffffff', '#c7d2fe'], desc: 'Des bestioles glacées qui glissent encore plus vite.' },
  sunset: { name: 'Coucher de soleil', price: 0.99, dirs: ['#ff5e62', '#ff9966', '#ffcd56', '#c471f5'], bg: ['#6a2a8c', '#ff9a6b', '#ffd36b', '#ff5e8a'], desc: 'Ambiance plage à 19 h. Sans le sable.' },
  messageA: { name: 'Message de A', price: 1.99, dirs: ['#f5f5f5', '#a3a3a3', '#e11d48', '#525252'], bg: ['#0a0a0a', '#1f1f1f', '#e11d48', '#737373'], mask: true, desc: 'Masquées, mystérieuses. Quelqu’un t’observe. — A' },
  smoothie: { name: 'Smoothie', price: 1.49, dirs: ['#ff4d6d', '#ffd60a', '#80ed99', '#ff8fab'], bg: ['#1f7a8c', '#7fe0c5', '#ffd60a', '#ff8fab'], desc: 'Vitaminées. Rien que de les voir, tu te sens mieux.' },
});

export const themeOf = id => THEMES[id] || THEMES.pastel;

/** Textes du jeu en français. Une autre langue = un autre fichier avec les mêmes clés. */
export const TEXTS = Object.freeze({
  exit: ['Bye !', 'Libre !', 'Ciao !', 'Enfin dehors !', 'Je file !', 'À plus !', 'Youpi !', 'Sayonara !', 'Adieu le bouchon !'],
  bump: ['Aïe !', 'Pousse-toi !', 'Hé, doucement !', 'Bouchon !', 'Ça coince !', 'Mon nez !', 'T’as pas vu ?!'],
  rock: ['Tok.', 'C’est un rocher.', 'Il ne bougera pas.', 'Inamovible.'],
  combo: ['x{n} ! Évacuation express !', 'x{n} ! Même pas le temps de dire au revoir.', 'x{n} ! Portes grandes ouvertes !', 'x{n} ! Fluide comme un lundi férié.'],
  win: ['Tout le monde est dehors !', 'Évacuation réussie. Les pompiers sont jaloux.', 'Salle vide. Tu peux éteindre la lumière.', 'Zéro bouchon. Bison Futé te salue.'],
  lose: ['Trop de bouchons. Tout le monde est coincé.', 'Embouteillage général. On recommence ?', 'Les bestioles sont vexées. Retente ta chance.'],
  messageA: ['Belle sortie. Je t’observe. — A', 'Tu croyais que personne ne verrait ce bouchon ? — A'],
  shield: 'Bouclier ! Bouchon gratuit.',
  ads: [['Ce jeu ressemble vraiment à sa pub.', 'Incroyable, non ?'], ['Ici, une vraie régie afficherait 5 secondes de pub.', 'C’est ce qui paie les serveurs.'], ['Achète un canapé.', 'Ou pas. On n’est pas ta mère.']],
  tips: {
    first: 'Touche une bestiole dont le chemin est libre : elle sort par son nez.',
    rocks: 'Nouveau : les rochers ne bougent jamais. Fais sortir les bestioles par un autre chemin.',
    hard: 'Niveau difficile ! Prends ton temps, le chrono ne compte pas ici.',
    shield: 'Série de 3 victoires : ton premier bouchon de ce niveau est gratuit.',
  },
});

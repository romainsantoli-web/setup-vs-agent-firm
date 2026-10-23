⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

# Architecture de Tous Dehors

## Principes

1. **JavaScript pur, sans framework ni dépendance.** Modules ES natifs, WebGL et Canvas 2D. Le même code tourne dans un navigateur, dans une TWA Google Play ou dans une app de bureau web (type Electron).
2. **La logique ne touche jamais le DOM.** `core/` et `game/` sont des fonctions pures ou des objets d'état. Ils tournent dans Node, ce qui permet de tout tester sans navigateur.
3. **Le rendu lit l'état, il ne le modifie pas.** `render/` dessine ce que la session lui donne.
4. **La session communique par événements.** `tap()` et `step()` renvoient des événements (`exit`, `bump`, `impact`, `cross`, `win`, `lose`…). Le contrôleur `main.js` les traduit en sons, particules et interface.
5. **Les règles promises aux joueurs sont du code testé.** Pubs, indices et prix vivent dans `core/economy.js`, couvert par des tests.

## Arborescence

```
games/tous-dehors/
├── index.html              fragment HTML (format Artifact), entouré par le build
├── manifest.webmanifest    PWA / TWA
├── styles/app.css          styles, jetons de couleur en variables CSS
├── assets/icon.svg         icône
├── src/
│   ├── main.js             contrôleur : écrans, boucle, liaison logique ↔ rendu
│   ├── core/               logique pure, testée
│   │   ├── rng.js          aléatoire déterministe (seed), clé de jour
│   │   ├── grid.js         directions, balayage d'une ligne de sortie
│   │   ├── generator.js    génération toujours soluble + solveur
│   │   ├── levels.js       courbe de difficulté, chapitres, défi du jour
│   │   ├── rules.js        étoiles, combos, séries, bouclier, rangs
│   │   ├── economy.js      pubs, indices, boutique du jour, événements, prix
│   │   ├── storage.js      sauvegarde validée champ par champ + migration
│   │   └── analytics.js    journal d'événements, branchable sur un outil externe
│   ├── game/session.js     état d'un niveau, règles et animations (sans DOM)
│   ├── render/
│   │   ├── gl.js           utilitaires WebGL et couleurs
│   │   ├── background.js   fond animé (shader WebGL, demi-résolution)
│   │   ├── particles.js    particules WebGL (pool préalloué, un seul tampon)
│   │   ├── sprites.js      dessin des bestioles et rochers, cache de sprites
│   │   └── board.js        plateau Canvas 2D
│   ├── audio/sfx.js        sons synthétisés en WebAudio
│   ├── ui/dom.js           fenêtres, toasts, pub simulée
│   ├── ui/icons.js         icônes SVG maison (pas d'emoji dans l'interface)
│   ├── services/leaderboard.js  classement (local, interface remplaçable)
│   └── config/             skins et textes (fr)
├── tests/                  node:test, sans dépendance
├── scripts/build.mjs       build de production vers dist/
└── docs/                   architecture, game design, marketing
```

## Performance

| Choix | Effet |
|---|---|
| Une seule boucle `requestAnimationFrame` | Pas de minuteries concurrentes, pas de saccades |
| Sprites pré-rendus en cache (skin × direction × expression × taille) | Le plateau ne fait que des `drawImage` |
| Fond WebGL à demi-résolution, une image sur deux | Économie de batterie, rendu flou voulu |
| Particules : pool préalloué + `Float32Array` réutilisé | Aucune allocation par image, pas de pause du ramasse-miettes |
| `devicePixelRatio` plafonné à 2 | Évite les canvas énormes sur écrans 3× |
| Repli sans WebGL | Dégradé CSS ; le jeu reste jouable |
| `prefers-reduced-motion` respecté | Moins de particules, pas de secousses |

## Générateur toujours soluble

Construction à rebours : chaque bestiole posée doit avoir une sortie libre à ce moment-là. L'ordre inverse de pose est une solution. Les rochers sont posés en premier et ne bougent jamais. Comme faire sortir une bestiole libre ne bloque jamais les autres, un solveur glouton suffit à vérifier une grille. Les tests génèrent 300 niveaux et le défi du jour, et vérifient qu'ils sont tous solubles.

## Données et vie privée

- Sauvegarde locale uniquement (`localStorage`), relue et filtrée champ par champ.
- Analytics locales pour l'instant : aucune donnée ne quitte l'appareil. Le paramètre `sink` permettra de brancher Firebase ou un outil d'éditeur, avec consentement.

## Commandes

```bash
npm test            # tests unitaires
npm run coverage    # tests + couverture (seuil 80 % lignes, branches, fonctions)
npm run build       # produit dist/
npm run serve       # build + serveur local sur http://localhost:8080
```

## Prochaines étapes techniques

1. **Emballage Google Play** : TWA avec Bubblewrap, icônes PNG 512 px et 192 px générées depuis `assets/icon.svg`, fichier `assetlinks.json` sur le domaine d'hébergement.
2. **Hors ligne** : service worker qui met en cache `dist/` (non utilisable dans l'aperçu Artifact, à activer en production).
3. **Classement mondial** : adaptateur Google Play Games Services ou Firebase derrière `services/leaderboard.js`.
4. **Régie pub et paiements réels** : Google Play Billing via la Digital Goods API dans la TWA ; régie pub à valider (compatibilité TWA non confirmée).

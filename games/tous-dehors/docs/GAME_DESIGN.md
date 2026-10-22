⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

# Game design de Tous Dehors

## Le concept en une phrase

Une grille de bestioles pressées : touche celles dont le chemin est libre pour les faire sortir, sans créer de bouchon.

## Boucle de jeu (30 à 60 secondes)

1. Lire la grille : chaque bestiole a un nez-flèche et une couleur par direction.
2. Trouver une bestiole libre et la toucher : elle file avec un son qui monte et une traînée lumineuse.
3. Enchaîner vite pour faire monter le combo (x3, x4…).
4. Se tromper coûte un cœur : la bestiole se cogne, râle, et revient à sa place.
5. Grille vide : étoiles, confettis, niveau suivant.

## Ce qui rend accro, et les limites qu'on se fixe

| Levier | Mise en œuvre | Limite volontaire |
|---|---|---|
| Sessions ultra-courtes | Niveaux de 30 à 60 s | — |
| Sensation de maîtrise | Combos, sons qui montent, secousses, confettis WebGL | — |
| Progression visible | Chapitres de 10 niveaux, pastilles de progression, rangs liés aux étoiles | — |
| Série de victoires | 3 victoires d'affilée : bouclier, le premier bouchon est gratuit | Perdre remet la série à zéro, sans rien coûter |
| Nouveauté régulière | Courbe en dents de scie (difficile tous les 5 niveaux, puis respiration), rochers au niveau 8 | Jamais de niveau impossible : tous sont solubles |
| Rendez-vous quotidien | Défi du jour partagé, chrono à partager | Pas de récompense de connexion ni de punition si on rate un jour |
| Collection | Skins cosmétiques, boutique du jour | Aucun avantage en jeu, prix en euros, pas de loot box |

Ces limites viennent de l'analyse des avis négatifs : niveaux truqués, corvées quotidiennes, pay-to-win et pubs forcées sont les premières causes de colère des joueurs.

## Courbe de difficulté

| Niveaux | Grille | Densité | Nouveauté |
|---|---|---|---|
| 1 à 3 | 4×4 | environ 55 % | Tutoriel : indice automatique au niveau 1 |
| 4 à 7 | 5×5 à 5×6 | 63 à 72 % | Niveau 5 : premier niveau « difficile » |
| 8 à 15 | 6×7 à 8×9 | 75 à 90 % | Rochers |
| 16 et plus | jusqu'à 8×10 | jusqu'à 90 % (95 % en difficile) | Plus de rochers, jusqu'à 6 |

Un niveau « difficile » tous les 5 niveaux, suivi d'un niveau « respiration » moins dense.

## Monétisation

| Source | Règle |
|---|---|
| Pub récompensée | Au choix : +1 cœur après une défaite, une seule fois par tentative |
| Pub imposée | Au plus une tous les 3 niveaux gagnés, aucune avant le niveau 11 |
| Sans pub imposée | 2,99 €, achat unique |
| Skins | 0,99 € à 1,99 €, cosmétiques, boutique du jour avec compte à rebours réel |
| Indices | Jamais vendus : 3 au départ, +1 toutes les 3 victoires, +2 par chapitre, +1 par défi du jour |

## Pistes pour la suite

- Nouvelles mécaniques : bestioles endormies (2 touches), glace (glisse puis s'arrête), tunnels.
- Événements saisonniers : Noël, Saint-Valentin, été.
- Duels asynchrones sur la même grille entre amis.
- Classement mondial du défi du jour.
- Skins créateurs avec partage de revenus.

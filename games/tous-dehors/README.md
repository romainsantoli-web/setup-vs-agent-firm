⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

# Tous Dehors

Puzzle de flèches mobile : touche les bestioles dont le chemin est libre pour les faire sortir, sans créer de bouchon.

- **Technique** : JavaScript pur, WebGL et Canvas 2D, sans dépendance. Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
- **Game design** : boucle de jeu, courbe de difficulté, monétisation. Voir [docs/GAME_DESIGN.md](docs/GAME_DESIGN.md).
- **Marketing** : lancement à moins de 50 €, fiche Google Play, scripts TikTok, éditeurs. Voir [docs/MARKETING.md](docs/MARKETING.md).

## Démarrer

Prérequis : Node 22 ou plus, Python 3 pour le serveur local.

```bash
npm test            # tests unitaires
npm run coverage    # couverture, seuil 80 %
npm run serve       # build puis http://localhost:8080
```

Ajouter `#debug` à l'adresse expose `window.__td` (bestioles libres, état, événements analytics) pour les tests automatisés.

## État

Prototype jouable. Achats et pubs simulés. Le nom « Tous Dehors » doit être vérifié (INPI, EUIPO) avant publication.

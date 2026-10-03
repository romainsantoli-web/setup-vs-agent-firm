# mft-crypto — pipeline de recherche MFT sur crypto-dérivés

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

Livre mid-frequency (10 s – 1 h) exécuté depuis le VPS de Londres. Commencer par **[RESEARCH.md](RESEARCH.md)**
(verdict, économie des paliers, carte des signaux, protocole, plan vers la production).

| module | rôle |
|---|---|
| `mft/models.py` | validation Pydantic de tous les inputs (slugs, symboles, path traversal) |
| `mft/fees.py` | barèmes de paliers Binance UM / Bybit / Hyperliquid (instantanés à vérifier) |
| `mft/edge_math.py` | économie analytique d'une politique à seuil : IC de break-even, IC combiné, IC requis pour un Sharpe |
| `mft/tiers.py` | point fixe volume → palier → seuil → volume ; rampe d'amorçage ; PnL à chaque palier |
| `mft/features.py` | 10 signaux pré-enregistrés, point-in-time |
| `mft/validation.py` | IC poolé, étude d'événements, contrôle de fuite, DSR, PBO, verdicts |
| `mft/combine.py` | combinaison walk-forward purgée (ridge, signes contraints) |
| `mft/backtest.py` | simulateur taker/maker : fills conservateurs, sélection adverse, funding, impact |
| `mft/synthetic.py` | marché synthétique planté / nul (banc de test du pipeline) |
| `mft/study.py` | orchestration de l'étude complète |
| `mft/data_sources.py` | archives publiques Binance/Bybit → barres |
| `mft/collector.py` | collecteur websocket live (liquidations, BBO, mark/funding/OI) |

```bash
pip install -e '.[dev]' websockets && python -m pytest
```

# Livre MFT crypto-dérivés — mémo de recherche n°1

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
> Aucun chiffre de ce mémo ne provient de données de marché réelles : l'environnement de travail
> n'avait pas accès aux exchanges (proxy 403 sur data.binance.vision, fapi.binance.com, api.bybit.com…).
> Les chiffres viennent (a) d'un modèle analytique des coûts et paliers, (b) d'un marché synthétique
> à effets plantés qui sert à valider le pipeline. Les barèmes de frais sont des instantanés à vérifier.

---

## 0. Mise à jour du 03/10 — exécution sur **Kraken Futures** (remplace Binance)

Binance n'offre pas ses perps aux résidents français. Le livre s'exécute donc sur **Kraken Futures**
(perps linéaires `PF_*`). Binance et Bybit restent des **sources d'information** (lead-lag,
liquidations), jamais des venues de trading. Les §1–2 ci-dessous (calculés pour Binance) sont
conservés comme point de comparaison ; les chiffres qui comptent sont ceux de cette section.

**Ce que le desk a déjà mesuré sur Kraken** (session MMXM, VPS Londres) :
- latence Londres → Kraken Futures : plancher aller simple 2,3 ms, médiane de réception des trades
  `PF_XBTUSD` 8,6 ms. Binance arrive à Londres en environ 112 ms (venue lointaine) ;
- market making sur flux public : −0,9 à −1,7 bp par fill ; **vrais ordres de Romain : −2,6 à
  −3 bp par fill**. C'est notre calibration de sélection adverse (`adverse_bps = 2,5`) ;
- perp en avance sur spot de 70 à 150 ms, mais 0,8–1,3 bp de gain, très en dessous des frais.
  Confirme que l'horizon sub-seconde est mort ;
- un enregistreur Kraken Futures (L1 + trades, 10 perps) et un Binance tournent sur le VPS jusqu'au
  13/10. **Pas besoin de déployer un nouveau collecteur pour Kraken** : on lit ces données.

**Barème Kraken Futures perps, VÉRIFIÉ le 03/10 par le desk depuis le VPS** (API publique) :

| volume 30 j | < 5 M$ | ≥ 5 M$ | ≥ 10 M$ | ≥ 25 M$ | ≥ 50 M$ | ≥ 100 M$ | ≥ 250 M$ | ≥ 1 Md$ |
|---|---|---|---|---|---|---|---|---|
| maker (bp) | 2,00 | 1,75 | 1,50 | 1,00 | 0,50 | 0 | −0,30 | −0,60 |
| taker (bp) | 5,00 | 4,50 | 4,00 | 3,00 | 2,50 | 2,00 | 1,75 | 1,35 |

Il existe aussi des barèmes « Incentive » (rabais maker jusqu'à −1 bp au-delà de 1 Md$) et
**« Consumer » à 25 bp maker ET taker**. Sur Consumer, l'IC de break-even à 1 h est d'environ
0,53 : **aucun livre MFT n'est viable**. Il faut donc d'abord savoir lequel s'applique au compte de
Romain, ce que seule l'API privée dit (le desk attend son accord direct pour l'interroger).

Levier max affiché (public) : 100× BTC/ETH/SOL, 50× XRP/DOGE/ADA/LINK/LTC/SUI/ZEC. Le levier
réellement autorisé à un particulier français via l'entité UE reste à lire sur le compte.

**IC combiné requis pour un Sharpe net ≥ 2** (barème vérifié, 10 perps, levier brut 3×, spread
3 bps, sélection adverse 2,5 bps mesurée, ADV 30 M$ ; `reports/tier_economics.md`) :

| capital | horizon | taker | entrée maker | maker 2 jambes (borne haute) |
|---|---|---|---|---|
| 100 k$ | 15 min | 0,174 (K1) | 0,142 (K1) | 0,100 (K2) |
| 100 k$ | 1 h | 0,112 (K1) | 0,098 (K1) | 0,072 (K2) |
| 250 k$ | 1 h | 0,120 (K2) | 0,101 (K2) | 0,066 (K3) |
| 1 M$ | 1 h | 0,144 (K4) | 0,107 (K4) | 0,054 (K5) |

**Ce que ça change :**
1. **Barre haute.** Les paliers réels démarrent à 5 M$ (et non 100 k$), donc le livre reste vers
   K0–K2 : il faut un IC combiné d'environ **0,10–0,12 à 1 h** en taker / entrée maker. Avec des
   signaux d'IC 0,03, c'est 12 à 16 signaux orthogonaux : irréaliste à court terme.
2. **Le maker 2 jambes n'est pas crédible** : le desk vient de montrer sur 14 jours Kraken que 76 %
   des fills passifs arrivent quand on est seul au niveau (le niveau va céder), avec −0,74 bp par
   fill dans le meilleur cas même à frais nuls.
3. **L'impact domine les frais** sur des carnets fins (~3,7 bps par jambe pour un clip de 75 k$).
   Capacité : 100–250 k$.
4. **Leviers réalistes**, par ordre : (a) écarter le risque « Consumer » (API privée) ;
   (b) allonger l'horizon vers 2–8 h, où le coût fixe pèse 2 à 3 fois moins par rapport à σ_h ;
   (c) négocier un barème Incentive ou VIP avec Kraken ; (d) le signal Binance/Bybit → Kraken
   (étude validée par Romain, en file chez le desk).
5. Funding Kraken **horaire** (le simulateur et le banc synthétique paient désormais à chaque heure).

**À vérifier avant tout trading :** barème et levier maximal accessibles via l'entité UE de Kraken
pour le profil de Romain (le levier brut de 3× est une hypothèse), sémantique du champ `side` des
liquidations dans le flux `trade` Kraken, unités de `relative_funding_rate`.

---

## 1. Verdict en une page

**Ce que l'arithmétique impose, avant tout signal :**

1. **L'horizon court est mort à notre palier.** À 1 min, il faut un IC combiné de 0,30 à 0,75 rien
   que pour payer les frais (table §2.1). À 5 min, il faut 0,14 à 0,22 pour un Sharpe net de 2.
   Ce sont des niveaux d'IC qui n'existent pas sur flux public. Notre terrain réel est donc
   **15 min – 1 h**, avec une **entrée passive**.
2. **La cible Sharpe ≥ 2 se traduit en une cible de recherche mesurable : l'IC combiné hors
   échantillon.** Avec 1 M$ de capital, levier brut 3×, 20 symboles et un horizon de 1 h, il faut
   un IC combiné de **0,079 en taker / 0,062 en entrée maker / 0,039 en maker des deux côtés**,
   au palier VIP3 que le livre atteint seul (§2.2). Avec des signaux décorrélés d'IC 0,02 à 0,03,
   il en faut **5 à 9** (IC combiné ≈ √Σ IC²). C'est ambitieux mais crédible, et c'est
   exactement le modèle « beaucoup de signaux faibles ».
3. **Le palier est un actif qu'on achète.** Un livre rentable au VIP3 mais pas au VIP0 ne trade pas
   au VIP0, ne génère aucun volume et **n'atteint jamais VIP3 par lui-même**. Le modèle calcule
   la rampe : coût et durée pour y arriver en faisant tourner la politique du palier cible
   (§2.3). C'est une décision d'investissement explicite, pas un effet de bord.
4. **Le maker est le levier n°1, mais aussi le principal risque de PnL fictif.** Notre banc
   synthétique l'a démontré (§5) : un modèle de fill naïf fabrique un Sharpe de 8 à 10 **sans aucun
   signal**. Pour nous, non colocalisés, un fill passif ne gagne pas le spread en moyenne. On
   l'impose (sélection adverse = demi-spread) jusqu'à le mesurer sur nos propres markouts.

**Ce qui est livré (dans `quant/mft-crypto/`, 57 tests, couverture 98 %) :**
pipeline de recherche complet (signaux pré-enregistrés → contrôle de fuite → IC poolé / étude
d'événements → verdicts corrigés des tests multiples → combinaison walk-forward purgée →
simulateur d'exécution taker/maker avec fills conservateurs et funding → point fixe des paliers),
collecteur live pour le VPS de Londres, téléchargeur d'archives, et un banc synthétique planté/nul
qui valide le tout.

**Prochaine action (bloquante) :** déployer le collecteur sur le VPS **aujourd'hui** (les
liquidations ne sont archivées nulle part sous forme exploitable) et lancer le backfill de 12 à
24 mois (§7).

---

## 2. Économie des frais et des paliers (Binance USDⓈ-M, instantané non vérifié)

Hypothèses de planification : vol annuelle 70 %, spread moyen 1 bp, 20 symboles, breadth
effective 6 (les cryptos sont très corrélées), levier brut 3×, taux de fill passif 60 %,
impact = 0,2 · σ_jour · √(clip/ADV) avec un ADV de 300 M$. Tout est paramétrable :
`python scripts/tier_economics.py --help`. Tables complètes : `reports/tier_economics.md`.

### 2.1 IC combiné minimal pour payer les coûts (seuil k = 1)

| horizon | σ_h | VIP0 taker/taker | VIP0 maker/taker | VIP3 taker/taker | VIP3 maker/taker | VIP9 maker/taker |
|---|---|---|---|---|---|---|
| 1 min | 9,7 bps | 0,747 | 0,543 | 0,503 | 0,367 | 0,183 |
| 5 min | 21,6 bps | 0,334 | 0,243 | 0,225 | 0,164 | 0,082 |
| 15 min | 37,4 bps | 0,193 | 0,140 | 0,130 | 0,095 | 0,047 |
| 1 h | 74,8 bps | 0,096 | 0,070 | 0,065 | 0,047 | 0,024 |

Le coût d'un aller-retour est fixe, alors que l'edge brut croît en σ_h ∝ √h : **chaque
multiplication par 4 de l'horizon divise par 2 l'IC requis**. C'est la règle « horizon de
détention > horizon de coût » rendue quantitative.

### 2.2 IC combiné requis pour un Sharpe net ≥ 2, au palier que le livre atteint seul

| capital | horizon | taker | entrée maker | maker 2 jambes (borne haute) |
|---|---|---|---|---|
| 250 k$ | 15 min | 0,128 (VIP0) | 0,096 (VIP1) | 0,056 (VIP2) |
| 250 k$ | 1 h | 0,079 (VIP1) | 0,064 (VIP1) | 0,042 (VIP2) |
| 1 M$ | 15 min | 0,124 (VIP3) | 0,089 (VIP3) | 0,049 (VIP3) |
| 1 M$ | 1 h | 0,079 (VIP3) | 0,062 (VIP3) | 0,039 (VIP3) |
| 5 M$ | 15 min | 0,146 (VIP3) | 0,103 (VIP3) | 0,042 (VIP5) |
| 5 M$ | 1 h | 0,097 (VIP3) | 0,073 (VIP3) | 0,034 (VIP5) |

À 5 M$, le taker se dégrade : l’impact sur des clips de 750 k$ coûte environ 3,7 bps par jambe, contre 1,6 bp à 1 M$.
Le sweet spot de capacité pour un livre directionnel sur 20 noms est donc **0,5 à 2 M$**. Au-delà,
il faut élargir l'univers ou exécuter en maker.

### 2.3 PnL à chaque palier : exemple 1 M$, horizon 15 min, IC 0,05, maker des deux côtés

| palier | coût AR (bps) | k | edge net (bps) | trades/j | volume 30 j | seuil du palier | auto-entretenu | PnL/an | Sharpe |
|---|---|---|---|---|---|---|---|---|---|
| VIP0 | 5,00 | 2,95 | 1,05 | 4 | 33 M$ | 0 | oui | 21 k$ | 0,56 |
| VIP1 | 4,20 | 2,58 | 1,21 | 12 | 104 M$ | 15 M$ | oui | 76 k$ | 1,15 |
| VIP2 | 3,80 | 2,38 | 1,27 | 20 | 182 M$ | 50 M$ | oui | 140 k$ | 1,59 |
| **VIP3** | 3,40 | 2,18 | 1,33 | 34 | 307 M$ | 100 M$ | **oui ← atteint** | 248 k$ | **2,17** |
| VIP4 | 3,00 | 1,98 | 1,40 | 56 | 500 M$ | 600 M$ | non | 425 k$ | 2,91 |
| VIP6 | 2,20 | 1,60 | 1,58 | 126 | 1,1 Md$ | 2,5 Md$ | non | 1,1 M$ | 4,98 |
| VIP9 | 1,00 | 1,05 | 1,93 | 338 | 3,0 Md$ | 25 Md$ | non | 3,6 M$ | 9,92 |

Lecture : chaque palier abaisse le coût, donc le seuil optimal k, ce qui augmente le nombre de
trades et le volume. Le livre grimpe seul jusqu'au VIP3 (chemin VIP0 → VIP1 → VIP3). Au-delà, son
propre volume ne suffit plus : **VIP4+ n'est atteignable qu'avec plus de capital, plus de noms, ou
un horizon plus court** (qui ne devient rentable qu'à ces paliers). C'est la boucle palier ↔ signal
que le module `tiers.py` résout explicitement.

Rampe d'amorçage (même scénario) : il faut **10 jours** pour passer de VIP0 à VIP3, avec un PnL de
rampe de +2,9 k$, donc rentable dès le départ. Pour 1 h, IC 0,08, taker : 23 jours et +14,9 k$.

### 2.4 Leviers de palier hors alpha

- **Concentrer tout le volume sur une seule venue** (Binance UM). Bybit sert de source de données
  pour le lead-lag et de venue de couverture, pas de venue de volume.
- Remises BNB sur les frais UM, programmes VIP « fast-track / match » sur preuve de volume chez un
  concurrent, programmes market-maker. **À vérifier, conditions changeantes.**
- La maker part (fraction maker du volume) compte pour certains programmes de rebates, et
  l'entrée passive nourrit les deux objectifs à la fois.

---

## 3. Qui perd l'argent que nous visons : carte des signaux

Règle : chaque signal est **pré-enregistré** (signe attendu, contrepartie, horizon) avant d'être
regardé. Un IC de mauvais signe tue le signal ; on ne le retourne jamais. Implémentés dans
`mft/features.py` (point-in-time vérifié par test) :

| # | signal | contrepartie (qui paie) | horizon | données | statut banc |
|---|---|---|---|---|---|
| 1 | `lead_lag` : mid de la venue leader − mid propre | arbitragistes contraints en latence/capital, marché fragmenté sans carnet consolidé | 1–15 min | BBO multi-venues horodaté chez nous | retrouvé |
| 2 | `btc_lead` : mouvement BTC × β pas encore dans l'alt | carnets d'alts qui se repricent lentement | 1–15 min | BBO / trades | retrouvé |
| 3 | `flow_imbalance` : déséquilibre agresseur | méta-ordres découpés (persistance du flux) | 5–60 min | aggTrades | retrouvé |
| 4 | `informed_flow` : gros prints − petits prints | détail agresseur vs taille informée | 5–60 min | aggTrades | retrouvé |
| 5 | `liquidation_reversal` : liquidations longues nettes / volume | **liquidations forcées du détail à levier** | 15–60 min | flux liquidations (collecteur) | retrouvé (étude d'événements) |
| 6 | `funding_crowding` : −z(funding prédit) | longs à levier entassés qui paient le carry | 1–8 h | markPrice@1s | retrouvé |
| 7 | `premium_reversion` : −z(prime perp/index) | arbitragistes de base contraints en capital | 15 min–4 h | mark/index | retrouvé |
| 8 | `short_term_reversal` | flux impatient qui paie l'immédiateté | 1–30 min | prix | leurre (correctement tué) |
| 9 | `momentum` 4 h | diffusion lente / suiveurs de tendance | 30 min–4 h | prix | faible |
| 10 | `oi_divergence` : ΔOI × signe(Δprix) | levier frais qui se dénoue | 30 min–4 h | metrics (OI 5 min) | leurre (correctement tué) |

**Backlog priorisé (les trois suivants à coder dès que des données réelles arrivent) :**

1. **Niveaux de liquidation publics Hyperliquid** : positions et prix de liquidation visibles
   on-chain. On peut construire une carte de densité de liquidations *ex ante* et prédire les
   cascades avant qu'elles arrivent (contrepartie : levier détail).
2. **Différentiels de funding entre venues** (Binance / Bybit / OKX / Hyperliquid) et
   micro-structure autour des règlements (00/08/16 UTC) : flux mécaniques de fermeture avant
   règlement (contrepartie : couvertures mécaniques).
3. **Prime Coinbase** (spot US vs perp offshore) et heures d'ouverture US / flux ETF : demande spot
   institutionnelle que les perps offshore intègrent avec retard.
4. Ensuite : expirations d'options Deribit (pinning / couverture gamma des dealers),
   rééquilibrages d'indices et listings/delistings, unlocks de tokens programmés, ouverture et
   clôture CME (gap de base), saisonnalité intraday par session (Asie / Europe / US) estimée en
   walk-forward.
5. **Variante cross-sectionnelle market-neutral** (long/short alts, β-hedgée BTC) pour chaque
   signal. La vol des résidus est plus faible et l'IC souvent plus haut, mais il y a deux jambes de
   coût. À arbitrer avec `tiers.py`.

**Autopsie d'un signal mort** (à remplir systématiquement) : le coût l'a-t-il tué (IC brut OK, net
négatif → horizon plus long, entrée maker) ? Décroissance (IC h1 > h2 → crowding, raccourcir la
mémoire) ? Régime (IC concentré dans un tercile de vol → signal conditionnel) ? Fuite (PIT > 0) ?
Chaque autopsie doit produire trois pistes.

---

## 4. Protocole de validation (non négociable)

| étape | outil | critère |
|---|---|---|
| Point-in-time | `validation.point_in_time_violations` | 0 violation, sinon verdict LEAK |
| IC | `validation.daily_ic` (rangs gaussiens globaux, contributions journalières) | t journalier, 1 jour = 1 observation |
| Signaux rares | `validation.event_study` (dé-chevauchement par symbole, cascades regroupées) | t sur clusters |
| Tests multiples | `validation.signal_verdict` (Bonferroni sur #signaux × #horizons) | KEEP seulement au-delà du seuil corrigé |
| Stabilité | IC première vs seconde moitié, `regime_ic` par tercile de vol | même signe partout |
| Combinaison | `combine.walk_forward_forecast` (fenêtre glissante, embargo = horizon, ridge, signes contraints) | IC combiné hors échantillon ≥ cible §2.2 |
| Sélection | `deflated_sharpe` (Bailey & López de Prado), `pbo_cscv` | DSR > 0,95 ; PBO < 0,2 |
| Banc nul | `synthetic.generate_market(planted=False)` | **aucun KEEP, PnL net < 0 dans tous les modes** |

Seuls les signaux **KEEP** entrent dans le livre. Les WEAK partent en incubation : on les
réévalue avec plus de données, ils ne sont jamais promus parce qu'ils « améliorent le backtest ».

---

## 5. Ce que le banc synthétique a attrapé (et que de vraies données auraient caché)

Le banc nul (même structure de marché, aucun effet prédictif, mêmes corrélations contemporaines
flux/prix) a trouvé **trois générateurs de PnL fictif** dans ma propre première version :

1. **Biais de l'IC intra-jour.** Calculer un IC de Spearman jour par jour sur un signal à fenêtre
   longue (momentum 4 h) donne IC = −0,10, t = −4,9 sur une **marche aléatoire pure**. Le
   démoyennage intra-jour de fenêtres qui se chevauchent fabrique de la mean-reversion.
   Correctif : moments globaux, contributions agrégées par jour. Test de régression :
   `test_intraday_ic_bias_on_random_walk_is_documented`.
2. **Capture de spread gratuite.** Des mèches de barre qui reviennent avant la clôture, combinées
   à un fill sans sélection adverse, donnent un Sharpe de 8 à 10 en `maker_both` **avec un IC nul**.
   C'est exactement l'illusion qui a tué le MM à 15 ms. Correctifs : extrêmes tirés d'un vrai pont
   brownien, fill seulement si le prix traverse le niveau, et sélection adverse imposée (demi-spread
   par fill passif) jusqu'à calibration sur nos markouts réels.
3. **Sur-comptage des liquidations.** Sur un panel (ts, symbole), le dé-chevauchement comptait des
   lignes et non des barres du symbole. Une même cascade était comptée plusieurs fois, d'où un
   t = 4,4 sur le marché nul. Correctif : dé-chevauchement par symbole et regroupement des
   événements simultanés.

S'y ajoute une contamination de feature : `btc_lead` défini comme « β·r_BTC − r_alt » portait la
reversal propre de l'alt et sortait avec le mauvais signe. Désormais, chaque exposition est un
signal séparé et c'est la combinaison qui les démêle.

Résultat actuel du banc (`reports/synthetic_study.md`, 6 symboles, 60 jours, h = 15 min) :

| exécution | VIP0 | VIP3 | VIP6 | VIP9 |
|---|---|---|---|---|
| marché planté, taker | SR −4,5 | SR 3,7 | SR 6,9 | SR 10,7 |
| marché planté, entrée maker | SR 3,2 | SR 9,2 | SR 12,2 | SR 15,3 |
| marché nul | aucun signal KEEP : pas de livre | | | |

Le banc reproduit qualitativement l'économie analytique : à IC combiné hors échantillon de 0,074 (7 signaux KEEP) et 15 min, le
taker exige VIP3+ alors que l'entrée maker est déjà rentable au VIP0. **Les niveaux de Sharpe
synthétiques ne sont pas des prévisions** : les effets plantés sont propres et stationnaires, ce que
le marché réel ne sera pas.

---

## 6. Exécution

- **Bande de non-trading** (hystérésis k_in / k_out) et **durée minimale de détention ≥ horizon
  du signal** : la rotation est pénalisée par construction.
- **Entrée passive par défaut** (`maker_entry`) : un ordre post-only au touch, expiré après N barres.
  On ne relance en taker (`chase_unfilled`) que si le signal est toujours au-dessus de k_in.
  `maker_both` est une borne haute : une sortie passive non remplie, c'est du risque non rémunéré.
- **Calibration obligatoire sur nos propres fills** : markout à 1 s / 10 s / 1 min / 5 min de chaque
  fill passif, puis fill rate par (symbole, distance au touch, volatilité). Ces deux nombres
  (`fill_rate`, `adverse_bps`) pilotent l'IC requis (§2.2) plus que n'importe quel signal.
- **Funding** : le simulateur paie ou encaisse le funding aux règlements. Les signaux 6/7 et le
  timing de sortie autour de 00/08/16 UTC doivent intégrer le funding prédit.
- **Latence** : 15 ms suffisent pour l'horizon visé. Le collecteur mesure notre distance réelle à
  chaque venue (`collector.latency_report`), avec NTP/chrony obligatoire sur le VPS.

---

## 7. Plan vers la production (avec critères de passage)

| phase | durée | contenu | critère pour passer |
|---|---|---|---|
| **P0 — Données** | J0 → S1 | collecteur sur VPS (systemd, top 20 perps Binance + Bybit) ; backfill `aggTrades`, `metrics`, `premiumIndexKlines`, `fundingRate` sur 12–24 mois ; NTP | 7 jours sans trou ; latences mesurées |
| **P1 — Recherche** | S1 → S6 | `signal_report` sur données réelles ; coder le backlog §3 (Hyperliquid, funding cross-venue, prime Coinbase) ; autopsies | ≥ 6 signaux KEEP à 15 min–1 h ; IC combiné hors échantillon ≥ cible §2.2 ; DSR > 0,95 ; PBO < 0,2 |
| **P2 — Ombre** | 3–4 sem. | prévisions live + ordres post-only de taille minimale pour mesurer fill rate et markouts réels ; réconciliation live vs backtest | écart de prévision live/backtest < 20 % ; `adverse_bps` et `fill_rate` mesurés et réinjectés |
| **P3 — Petit live** | 4–6 sem. | 50–100 k$, levier 1× ; kill-switches actifs | implementation shortfall < 30 % de l'edge brut ; Sharpe live compatible avec le backtest à 2σ |
| **P4 — Montée en palier** | ensuite | décision de rampe chiffrée par `tiers.analytic_book` / `simulated_tier_table` ; capital vers 0,5–2 M$ | palier visé auto-entretenu ; Sharpe net ≥ 2 sur 3 mois glissants |

**Risque (dès P3)** : perte journalière max, drawdown max (3σ du PnL attendu), exposition brute
et nette par symbole, détection de flux périmé (pas de BBO depuis X s → flat), santé de l'exchange
(spread anormal, statut maintenance), clés API sans retrait, liste blanche d'IP du VPS, secrets
masqués dans les logs.

Déploiement du collecteur (exemple de unit systemd) :

```ini
[Service]
ExecStart=/opt/mft/.venv/bin/python /opt/mft/quant/mft-crypto/scripts/collect.py \
  --symbols BTCUSDT ETHUSDT SOLUSDT XRPUSDT DOGEUSDT BNBUSDT ADAUSDT AVAXUSDT LINKUSDT SUIUSDT \
  --out-dir /data/live
Restart=always
RestartSec=5
```

---

## 8. Limites et points à vérifier

- **Aucune donnée réelle n'a été traitée.** Le réseau de l'environnement bloquait les exchanges.
  Pour l'ouvrir : Network access → Custom, ajouter `data.binance.vision`, `fapi.binance.com`,
  `fstream.binance.com`, `api.bybit.com`, `stream.bybit.com`, `public.bybit.com`.
- **Barèmes de frais** (`mft/fees.py`) reconstruits de mémoire (`verified=False`), à vérifier avant
  toute décision, en particulier les seuils VIP et les conditions BNB.
- **Sémantique du champ `S` des liquidations Bybit** : codée selon la doc (« Buy = long
  liquidé »). À valider sur données live (direction du prix autour du print) ; le drapeau
  `BYBIT_LIQ_BUY_IS_LONG` le permet.
- **Le modèle analytique** suppose des trades indépendants, une breadth effective de 6 et un
  coefficient d'impact de 0,2. Le Sharpe varie en √breadth, donc à recalibrer sur la corrélation
  réelle des PnL par symbole.
- **Le simulateur est en barres** : il ne voit ni la position dans la file ni la profondeur. D'où
  la sélection adverse imposée ; un simulateur L2 event-driven sera nécessaire avant P3 pour les
  stratégies à entrée maker.

---

## 9. Commandes

```bash
cd quant/mft-crypto
pip install -e '.[dev]' websockets
python -m pytest                                   # 57 tests, couverture ≥ 80 % imposée
python scripts/tier_economics.py                   # → reports/tier_economics.md
python scripts/run_study.py --n-days 60            # → reports/synthetic_study.md (banc planté + nul)
python scripts/download_public_data.py --venue binance_um --dataset aggTrades \
    --symbol BTCUSDT --start 2025-01-01 --end 2025-03-31 --out-dir data/raw
python scripts/collect.py --symbols BTCUSDT ETHUSDT --out-dir data/live
```

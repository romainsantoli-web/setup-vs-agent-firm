# Économie des paliers de frais — livre MFT

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
> Barème `binance_um` (2025-snapshot, vérifié=False). Hypothèses : 20 symboles, breadth effective 6.0, vol annuelle 70%, spread moyen 1.0 bps, levier brut 3.0x, taux de fill passif 60%, sélection adverse = demi-spread par jambe passive.

## 1. IC combiné minimal (break-even à k=1) par horizon et palier

| horizon | σ_h (bps) | VIP0 taker/taker | VIP0 maker/taker | VIP3 taker/taker | VIP3 maker/taker | VIP6 taker/taker | VIP6 maker/taker | VIP9 taker/taker | VIP9 maker/taker |
|---|---|---|---|---|---|---|---|---|---|
| 1m | 9.7 | 0.747 | 0.543 | 0.503 | 0.367 | 0.407 | 0.278 | 0.299 | 0.183 |
| 5m | 21.6 | 0.334 | 0.243 | 0.225 | 0.164 | 0.182 | 0.125 | 0.134 | 0.082 |
| 15m | 37.4 | 0.193 | 0.140 | 0.130 | 0.095 | 0.105 | 0.072 | 0.077 | 0.047 |
| 1h | 74.8 | 0.096 | 0.070 | 0.065 | 0.047 | 0.053 | 0.036 | 0.039 | 0.024 |

## 2. IC combiné requis pour un Sharpe net ≥ 2 (au palier que le livre atteint seul)

| capital | horizon | taker | maker_entry | maker_both |
|---|---|---|---|---|
| 250.0k | 5m | 0.187 (VIP0) | 0.143 (VIP0) | 0.082 (VIP3) |
| 250.0k | 15m | 0.128 (VIP0) | 0.096 (VIP1) | 0.056 (VIP2) |
| 250.0k | 1h | 0.079 (VIP1) | 0.064 (VIP1) | 0.042 (VIP2) |
| 1.0M | 5m | 0.196 (VIP3) | 0.138 (VIP3) | 0.072 (VIP3) |
| 1.0M | 15m | 0.124 (VIP3) | 0.089 (VIP3) | 0.049 (VIP3) |
| 1.0M | 1h | 0.079 (VIP3) | 0.062 (VIP3) | 0.039 (VIP3) |
| 5.0M | 5m | 0.216 (VIP3) | 0.148 (VIP3) | 0.063 (VIP8) |
| 5.0M | 15m | 0.146 (VIP3) | 0.103 (VIP3) | 0.042 (VIP5) |
| 5.0M | 1h | 0.097 (VIP3) | 0.073 (VIP3) | 0.034 (VIP5) |

## 3. Palier atteint et PnL — capital 1M$

| horizon | IC combiné | exécution | chemin organique | palier atteint | PnL/an | Sharpe | meilleur palier soutenable | PnL/an | Sharpe | rampe (jours / PnL) | payback (j) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.03 | taker | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.03 | maker_entry | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.03 | maker_both | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.05 | taker | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.05 | maker_entry | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.05 | maker_both | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.08 | taker | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.08 | maker_entry | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.08 | maker_both | VIP0 → VIP1 → VIP3 → VIP4 → VIP5 | VIP5 | 1.5M | 9.20 | VIP6 | 2.5M | 12.29 | 26 / 82.8k | 0 |
| 15m | 0.03 | taker | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.03 | maker_entry | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.03 | maker_both | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.05 | taker | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.05 | maker_entry | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.05 | maker_both | VIP0 → VIP1 → VIP3 | VIP3 | 248.3k | 2.17 | VIP3 | 248.3k | 2.17 | 10 / 2.9k | 0 |
| 15m | 0.08 | taker | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.08 | maker_entry | VIP0 | VIP0 | 4.9k | 0.32 | VIP1 | 25.9k | 0.78 | 18 / 195 | 0 |
| 15m | 0.08 | maker_both | VIP0 → VIP3 → VIP5 | VIP5 | 3.2M | 11.27 | VIP5 | 3.2M | 11.27 | 16 / 101.5k | 0 |
| 1h | 0.03 | taker | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.03 | maker_entry | VIP0 | VIP0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.03 | maker_both | VIP0 → VIP1 → VIP2 → VIP3 | VIP3 | 156.4k | 0.98 | VIP3 | 156.4k | 0.98 | 21 / 5.0k | 0 |
| 1h | 0.05 | taker | VIP0 | VIP0 | 254 | 0.04 | VIP0 | 254 | 0.04 | 0 / 0 | -0 |
| 1h | 0.05 | maker_entry | VIP0 | VIP0 | 14.0k | 0.33 | VIP1 | 43.8k | 0.61 | 16 / 802 | 0 |
| 1h | 0.05 | maker_both | VIP0 → VIP3 | VIP3 | 921.3k | 3.37 | VIP3 | 921.3k | 3.37 | 7 / 13.3k | 0 |
| 1h | 0.08 | taker | VIP0 → VIP1 → VIP2 → VIP3 | VIP3 | 358.3k | 2.35 | VIP3 | 358.3k | 2.35 | 23 / 14.9k | 0 |
| 1h | 0.08 | maker_entry | VIP0 → VIP3 | VIP3 | 876.6k | 3.99 | VIP3 | 876.6k | 3.99 | 11 / 20.5k | 0 |
| 1h | 0.08 | maker_both | VIP0 → VIP3 → VIP4 | VIP4 | 3.0M | 8.19 | VIP4 | 3.0M | 8.19 | 23 / 173.1k | 0 |

## 4. Tables complètes : PnL à chaque palier (capital 1M$, IC 0,05)

### horizon 5m, taker

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 **←** | 14.28 | 1.64 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| VIP1 | 12.28 | 1.64 | inf | 0.00 | 0 | 0 | 15.0M | no | 0 | 0% | 0.00 |
| VIP2 | 11.28 | 1.64 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| VIP3 | 10.68 | 1.64 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| VIP4 | 10.28 | 1.64 | inf | 0.00 | 0 | 0 | 600.0M | no | 0 | 0% | 0.00 |
| VIP5 | 9.68 | 1.64 | inf | 0.00 | 0 | 0 | 1.0B | no | 0 | 0% | 0.00 |
| VIP6 | 9.28 | 1.64 | inf | 0.00 | 0 | 0 | 2.5B | no | 0 | 0% | 0.00 |
| VIP7 | 8.68 | 1.64 | inf | 0.00 | 0 | 0 | 5.0B | no | 0 | 0% | 0.00 |
| VIP8 | 8.28 | 1.64 | inf | 0.00 | 0 | 0 | 12.5B | no | 0 | 0% | 0.00 |
| VIP9 | 7.68 | 1.64 | inf | 0.00 | 0 | 0 | 25.0B | no | 0 | 0% | 0.00 |

### horizon 5m, maker_entry

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 **←** | 9.64 | 1.64 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| VIP1 | 8.24 | 1.64 | inf | 0.00 | 0 | 0 | 15.0M | no | 0 | 0% | 0.00 |
| VIP2 | 7.54 | 1.64 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| VIP3 | 7.04 | 1.64 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| VIP4 | 6.64 | 1.64 | inf | 0.00 | 0 | 0 | 600.0M | no | 0 | 0% | 0.00 |
| VIP5 | 6.14 | 1.64 | inf | 0.00 | 0 | 0 | 1.0B | no | 0 | 0% | 0.00 |
| VIP6 | 5.74 | 1.64 | inf | 0.00 | 0 | 0 | 2.5B | no | 0 | 0% | 0.00 |
| VIP7 | 5.24 | 1.64 | inf | 0.00 | 0 | 0 | 5.0B | no | 0 | 0% | 0.00 |
| VIP8 | 4.84 | 1.64 | inf | 0.00 | 0 | 0 | 12.5B | no | 0 | 0% | 0.00 |
| VIP9 | 4.34 | 1.64 | 4.00 | 0.22 | 0 | 2.0M | 25.0B | no | 267 | 0% | 0.05 |

### horizon 5m, maker_both

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 **←** | 5.00 | 1.64 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| VIP1 | 4.20 | 1.64 | 4.00 | 0.36 | 0 | 2.0M | 15.0M | no | 433 | 0% | 0.08 |
| VIP2 | 3.80 | 1.64 | 3.75 | 0.50 | 1 | 5.5M | 50.0M | no | 1.7k | 0% | 0.19 |
| VIP3 | 3.40 | 1.64 | 3.40 | 0.55 | 2 | 21.0M | 100.0M | no | 7.0k | 1% | 0.41 |
| VIP4 | 3.00 | 1.64 | 3.05 | 0.59 | 8 | 71.2M | 600.0M | no | 25.7k | 3% | 0.81 |
| VIP5 | 2.60 | 1.64 | 2.73 | 0.67 | 22 | 200.0M | 1.0B | no | 81.5k | 8% | 1.53 |
| VIP6 | 2.20 | 1.64 | 2.38 | 0.72 | 61 | 545.8M | 2.5B | no | 240.6k | 24% | 2.74 |
| VIP7 | 1.80 | 1.64 | 2.02 | 0.79 | 148 | 1.3B | 5.0B | no | 637.4k | 64% | 4.64 |
| VIP8 | 1.40 | 1.64 | 1.70 | 0.88 | 308 | 2.8B | 12.5B | no | 1.5M | 148% | 7.47 |
| VIP9 | 1.00 | 1.64 | 1.38 | 0.98 | 585 | 5.3B | 25.0B | no | 3.1M | 313% | 11.47 |

### horizon 15m, taker

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 **←** | 14.28 | 1.64 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| VIP1 | 12.28 | 1.64 | inf | 0.00 | 0 | 0 | 15.0M | no | 0 | 0% | 0.00 |
| VIP2 | 11.28 | 1.64 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| VIP3 | 10.68 | 1.64 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| VIP4 | 10.28 | 1.64 | inf | 0.00 | 0 | 0 | 600.0M | no | 0 | 0% | 0.00 |
| VIP5 | 9.68 | 1.64 | inf | 0.00 | 0 | 0 | 1.0B | no | 0 | 0% | 0.00 |
| VIP6 | 9.28 | 1.64 | inf | 0.00 | 0 | 0 | 2.5B | no | 0 | 0% | 0.00 |
| VIP7 | 8.68 | 1.64 | inf | 0.00 | 0 | 0 | 5.0B | no | 0 | 0% | 0.00 |
| VIP8 | 8.28 | 1.64 | inf | 0.00 | 0 | 0 | 12.5B | no | 0 | 0% | 0.00 |
| VIP9 | 7.68 | 1.64 | 4.00 | 0.22 | 0 | 1.1M | 25.0B | no | 149 | 0% | 0.02 |

### horizon 15m, maker_entry

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 **←** | 9.64 | 1.64 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| VIP1 | 8.24 | 1.64 | inf | 0.00 | 0 | 0 | 15.0M | no | 0 | 0% | 0.00 |
| VIP2 | 7.54 | 1.64 | 4.00 | 0.36 | 0 | 656.7k | 50.0M | no | 145 | 0% | 0.03 |
| VIP3 | 7.04 | 1.64 | 4.00 | 0.86 | 0 | 656.7k | 100.0M | no | 344 | 0% | 0.07 |
| VIP4 | 6.64 | 1.64 | 3.78 | 0.86 | 0 | 1.7M | 600.0M | no | 870 | 0% | 0.10 |
| VIP5 | 6.14 | 1.64 | 3.53 | 0.92 | 0 | 4.4M | 1.0B | no | 2.5k | 0% | 0.18 |
| VIP6 | 5.74 | 1.64 | 3.33 | 0.97 | 1 | 9.2M | 2.5B | no | 5.4k | 1% | 0.27 |
| VIP7 | 5.24 | 1.64 | 3.08 | 1.03 | 2 | 21.8M | 5.0B | no | 13.7k | 1% | 0.45 |
| VIP8 | 4.84 | 1.64 | 2.88 | 1.08 | 5 | 41.9M | 12.5B | no | 27.6k | 3% | 0.65 |
| VIP9 | 4.34 | 1.64 | 2.62 | 1.15 | 10 | 89.8M | 25.0B | no | 63.0k | 6% | 1.02 |

### horizon 15m, maker_both

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 | 5.00 | 1.64 | 2.95 | 1.05 | 4 | 32.9M | 0 | yes | 21.1k | 2% | 0.56 |
| VIP1 | 4.20 | 1.64 | 2.58 | 1.21 | 12 | 103.9M | 15.0M | yes | 76.2k | 8% | 1.15 |
| VIP2 | 3.80 | 1.64 | 2.38 | 1.27 | 20 | 181.9M | 50.0M | yes | 140.1k | 14% | 1.59 |
| VIP3 **←** | 3.40 | 1.64 | 2.18 | 1.33 | 34 | 307.2M | 100.0M | yes | 248.3k | 25% | 2.17 |
| VIP4 | 3.00 | 1.64 | 1.98 | 1.40 | 56 | 500.4M | 600.0M | no | 425.0k | 42% | 2.91 |
| VIP5 | 2.60 | 1.64 | 1.80 | 1.51 | 83 | 745.1M | 1.0B | no | 683.7k | 68% | 3.84 |
| VIP6 | 2.20 | 1.64 | 1.60 | 1.58 | 126 | 1.1B | 2.5B | no | 1.1M | 110% | 4.98 |
| VIP7 | 1.80 | 1.64 | 1.43 | 1.71 | 178 | 1.6B | 5.0B | no | 1.7M | 166% | 6.36 |
| VIP8 | 1.40 | 1.64 | 1.23 | 1.79 | 254 | 2.3B | 12.5B | no | 2.5M | 250% | 8.00 |
| VIP9 | 1.00 | 1.64 | 1.05 | 1.93 | 338 | 3.0B | 25.0B | no | 3.6M | 357% | 9.92 |

### horizon 1h, taker

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 **←** | 14.28 | 1.64 | 4.00 | 1.52 | 0 | 273.6k | 0 | yes | 254 | 0% | 0.04 |
| VIP1 | 12.28 | 1.64 | 3.53 | 1.84 | 0 | 1.8M | 15.0M | no | 2.0k | 0% | 0.12 |
| VIP2 | 11.28 | 1.64 | 3.28 | 1.96 | 1 | 4.6M | 50.0M | no | 5.4k | 1% | 0.20 |
| VIP3 | 10.68 | 1.64 | 3.12 | 2.04 | 1 | 7.7M | 100.0M | no | 9.5k | 1% | 0.26 |
| VIP4 | 10.28 | 1.64 | 3.03 | 2.09 | 1 | 10.7M | 600.0M | no | 13.6k | 1% | 0.32 |
| VIP5 | 9.68 | 1.64 | 2.88 | 2.17 | 2 | 17.5M | 1.0B | no | 23.0k | 2% | 0.42 |
| VIP6 | 9.28 | 1.64 | 2.78 | 2.22 | 3 | 23.8M | 2.5B | no | 32.2k | 3% | 0.51 |
| VIP7 | 8.68 | 1.64 | 2.62 | 2.31 | 4 | 37.4M | 5.0B | no | 52.5k | 5% | 0.66 |
| VIP8 | 8.28 | 1.64 | 2.53 | 2.36 | 6 | 50.0M | 12.5B | no | 71.9k | 7% | 0.78 |
| VIP9 | 7.68 | 1.64 | 2.38 | 2.45 | 8 | 75.8M | 25.0B | no | 113.2k | 11% | 1.00 |

### horizon 1h, maker_entry

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 **←** | 9.64 | 1.64 | 2.88 | 2.21 | 1 | 10.5M | 0 | yes | 14.0k | 1% | 0.33 |
| VIP1 | 8.24 | 1.64 | 2.53 | 2.40 | 3 | 30.0M | 15.0M | yes | 43.8k | 4% | 0.61 |
| VIP2 | 7.54 | 1.64 | 2.35 | 2.51 | 5 | 48.7M | 50.0M | no | 74.2k | 7% | 0.82 |
| VIP3 | 7.04 | 1.64 | 2.23 | 2.59 | 8 | 67.6M | 100.0M | no | 106.4k | 11% | 0.99 |
| VIP4 | 6.64 | 1.64 | 2.12 | 2.65 | 10 | 87.1M | 600.0M | no | 140.4k | 14% | 1.15 |
| VIP5 | 6.14 | 1.64 | 2.02 | 2.82 | 12 | 111.1M | 1.0B | no | 190.5k | 19% | 1.39 |
| VIP6 | 5.74 | 1.64 | 1.93 | 2.89 | 16 | 140.6M | 2.5B | no | 247.0k | 25% | 1.60 |
| VIP7 | 5.24 | 1.64 | 1.80 | 2.98 | 21 | 186.3M | 5.0B | no | 337.5k | 34% | 1.90 |
| VIP8 | 4.84 | 1.64 | 1.70 | 3.05 | 26 | 231.0M | 12.5B | no | 429.1k | 43% | 2.16 |
| VIP9 | 4.34 | 1.64 | 1.58 | 3.15 | 33 | 298.7M | 25.0B | no | 572.6k | 57% | 2.54 |

### horizon 1h, maker_both

| tier | RT cost (bps) | impact/jambe | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VIP0 | 5.00 | 1.64 | 1.75 | 3.05 | 23 | 207.7M | 0 | yes | 385.8k | 39% | 2.05 |
| VIP1 | 4.20 | 1.64 | 1.55 | 3.21 | 35 | 314.0M | 15.0M | yes | 613.0k | 61% | 2.65 |
| VIP2 | 3.80 | 1.64 | 1.45 | 3.29 | 42 | 381.2M | 50.0M | yes | 763.1k | 76% | 3.00 |
| VIP3 **←** | 3.40 | 1.64 | 1.38 | 3.45 | 49 | 438.4M | 100.0M | yes | 921.3k | 92% | 3.37 |
| VIP4 | 3.00 | 1.64 | 1.28 | 3.54 | 58 | 524.4M | 600.0M | no | 1.1M | 113% | 3.78 |
| VIP5 | 2.60 | 1.64 | 1.18 | 3.63 | 69 | 622.1M | 1.0B | no | 1.4M | 138% | 4.23 |
| VIP6 | 2.20 | 1.64 | 1.10 | 3.80 | 78 | 703.3M | 2.5B | no | 1.6M | 163% | 4.71 |
| VIP7 | 1.80 | 1.64 | 1.00 | 3.90 | 91 | 822.5M | 5.0B | no | 2.0M | 195% | 5.22 |
| VIP8 | 1.40 | 1.64 | 0.93 | 4.08 | 102 | 920.1M | 12.5B | no | 2.3M | 228% | 5.77 |
| VIP9 | 1.00 | 1.64 | 0.83 | 4.19 | 118 | 1.1B | 25.0B | no | 2.7M | 270% | 6.36 |


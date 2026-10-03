# Économie des paliers de frais — livre MFT

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
> Barème `kraken_futures` (2026-10-03 API, vérifié=True). Hypothèses : 10 symboles, breadth effective 4.0, vol annuelle 70%, spread moyen 3.0 bps, levier brut 3.0x, taux de fill passif 60%, sélection adverse 2.5 bps par jambe passive (mesurée sur fills réels Kraken), ADV 30.0M$, coefficient d'impact 0.2.

## 1. IC combiné minimal (break-even à k=1) par horizon et palier

| horizon | σ_h (bps) | K0 taker/taker | K0 maker/taker | K3 taker/taker | K3 maker/taker | K6 taker/taker | K6 maker/taker | K7 taker/taker | K7 maker/taker |
|---|---|---|---|---|---|---|---|---|---|
| 1m | 9.7 | 0.883 | 0.747 | 0.611 | 0.543 | 0.441 | 0.370 | 0.387 | 0.323 |
| 5m | 21.6 | 0.395 | 0.334 | 0.273 | 0.243 | 0.197 | 0.166 | 0.173 | 0.144 |
| 15m | 37.4 | 0.228 | 0.193 | 0.158 | 0.140 | 0.114 | 0.096 | 0.100 | 0.083 |
| 1h | 74.8 | 0.114 | 0.096 | 0.079 | 0.070 | 0.057 | 0.048 | 0.050 | 0.042 |

## 2. IC combiné requis pour un Sharpe net ≥ 2 (au palier que le livre atteint seul)

| capital | horizon | taker | maker_entry | maker_both |
|---|---|---|---|---|
| 100.0k | 5m | 0.256 (K0) | 0.209 (K0) | 0.144 (K1) |
| 100.0k | 15m | 0.174 (K1) | 0.142 (K1) | 0.100 (K2) |
| 100.0k | 1h | 0.112 (K1) | 0.098 (K1) | 0.072 (K2) |
| 250.0k | 5m | 0.286 (K1) | 0.217 (K1) | 0.136 (K2) |
| 250.0k | 15m | 0.187 (K2) | 0.145 (K2) | 0.094 (K4) |
| 250.0k | 1h | 0.120 (K2) | 0.101 (K2) | 0.066 (K3) |
| 1.0M | 5m | 0.354 (K2) | 0.251 (K5) | 0.119 (K7) |
| 1.0M | 15m | 0.235 (K4) | 0.163 (K4) | 0.078 (K6) |
| 1.0M | 1h | 0.144 (K4) | 0.107 (K4) | 0.054 (K5) |

## 3. Palier atteint et PnL — capital 250.0k$

| horizon | IC combiné | exécution | chemin organique | palier atteint | PnL/an | Sharpe | meilleur palier soutenable | PnL/an | Sharpe | rampe (jours / PnL) | payback (j) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.03 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.03 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.03 | maker_both | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.05 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.05 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.05 | maker_both | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.08 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.08 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 5m | 0.08 | maker_both | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.03 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.03 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.03 | maker_both | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.05 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.05 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.05 | maker_both | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.08 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.08 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 15m | 0.08 | maker_both | K0 | K0 | 2.6k | 0.40 | K5 | 142.1k | 3.48 | 29 / 1.8k | 0 |
| 1h | 0.03 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.03 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.03 | maker_both | K0 | K0 | 12 | 0.01 | K0 | 12 | 0.01 | 0 / 0 | -0 |
| 1h | 0.05 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.05 | maker_entry | K0 | K0 | 28 | 0.02 | K0 | 28 | 0.02 | 0 / 0 | -0 |
| 1h | 0.05 | maker_both | K0 | K0 | 6.1k | 0.36 | K1 | 8.8k | 0.45 | 25 / 478 | 0 |
| 1h | 0.08 | taker | K0 | K0 | 511 | 0.12 | K0 | 511 | 0.12 | 0 / 0 | -0 |
| 1h | 0.08 | maker_entry | K0 | K0 | 8.4k | 0.54 | K1 | 12.5k | 0.66 | 27 / 735 | 0 |
| 1h | 0.08 | maker_both | K0 → K3 → K4 | K4 | 309.9k | 3.97 | K5 | 426.8k | 4.77 | 24 / 18.8k | 0 |

## 4. Tables complètes : PnL à chaque palier (capital 250.0k$, IC 0,05)

### horizon 5m, taker

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 20.33 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 19.33 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K2 | 18.33 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K3 | 16.33 | 3.66 | inf | 0.00 | 0 | 0 | 25.0M | no | 0 | 0% | 0.00 |
| K4 | 15.33 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K5 | 14.33 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| K6 | 13.83 | 3.66 | inf | 0.00 | 0 | 0 | 250.0M | no | 0 | 0% | 0.00 |
| K7 | 13.03 | 3.66 | inf | 0.00 | 0 | 0 | 1.0B | no | 0 | 0% | 0.00 |

### horizon 5m, maker_entry

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 14.66 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 13.91 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K2 | 13.16 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K3 | 11.66 | 3.66 | inf | 0.00 | 0 | 0 | 25.0M | no | 0 | 0% | 0.00 |
| K4 | 10.66 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K5 | 9.66 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| K6 | 9.11 | 3.66 | inf | 0.00 | 0 | 0 | 250.0M | no | 0 | 0% | 0.00 |
| K7 | 8.41 | 3.66 | inf | 0.00 | 0 | 0 | 1.0B | no | 0 | 0% | 0.00 |

### horizon 5m, maker_both

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 9.00 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 8.50 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K2 | 8.00 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K3 | 7.00 | 3.66 | inf | 0.00 | 0 | 0 | 25.0M | no | 0 | 0% | 0.00 |
| K4 | 6.00 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K5 | 5.00 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| K6 | 4.40 | 3.66 | 4.00 | 0.16 | 0 | 492.6k | 250.0M | no | 48 | 0% | 0.03 |
| K7 | 3.80 | 3.66 | 3.75 | 0.50 | 0 | 1.4M | 1.0B | no | 422 | 0% | 0.16 |

### horizon 15m, taker

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 20.33 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 19.33 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K2 | 18.33 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K3 | 16.33 | 3.66 | inf | 0.00 | 0 | 0 | 25.0M | no | 0 | 0% | 0.00 |
| K4 | 15.33 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K5 | 14.33 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| K6 | 13.83 | 3.66 | inf | 0.00 | 0 | 0 | 250.0M | no | 0 | 0% | 0.00 |
| K7 | 13.03 | 3.66 | inf | 0.00 | 0 | 0 | 1.0B | no | 0 | 0% | 0.00 |

### horizon 15m, maker_entry

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 14.66 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 13.91 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K2 | 13.16 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K3 | 11.66 | 3.66 | inf | 0.00 | 0 | 0 | 25.0M | no | 0 | 0% | 0.00 |
| K4 | 10.66 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K5 | 9.66 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |
| K6 | 9.11 | 3.66 | inf | 0.00 | 0 | 0 | 250.0M | no | 0 | 0% | 0.00 |
| K7 | 8.41 | 3.66 | inf | 0.00 | 0 | 0 | 1.0B | no | 0 | 0% | 0.00 |

### horizon 15m, maker_both

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 9.00 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 8.50 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K2 | 8.00 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K3 | 7.00 | 3.66 | 3.98 | 0.86 | 0 | 182.4k | 25.0M | no | 95 | 0% | 0.06 |
| K4 | 6.00 | 3.66 | 3.48 | 0.97 | 0 | 1.3M | 50.0M | no | 781 | 0% | 0.17 |
| K5 | 5.00 | 3.66 | 2.95 | 1.05 | 2 | 8.2M | 100.0M | no | 5.3k | 2% | 0.46 |
| K6 | 4.40 | 3.66 | 2.65 | 1.13 | 5 | 20.9M | 250.0M | no | 14.4k | 6% | 0.79 |
| K7 | 3.80 | 3.66 | 2.38 | 1.27 | 10 | 45.5M | 1.0B | no | 35.0k | 14% | 1.30 |

### horizon 1h, taker

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 20.33 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 19.33 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K2 | 18.33 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K3 | 16.33 | 3.66 | inf | 0.00 | 0 | 0 | 25.0M | no | 0 | 0% | 0.00 |
| K4 | 15.33 | 3.66 | 4.00 | 0.47 | 0 | 68.4k | 50.0M | no | 20 | 0% | 0.01 |
| K5 | 14.33 | 3.66 | 4.00 | 1.47 | 0 | 68.4k | 100.0M | no | 61 | 0% | 0.03 |
| K6 | 13.83 | 3.66 | 3.93 | 1.71 | 0 | 93.7k | 250.0M | no | 97 | 0% | 0.04 |
| K7 | 13.03 | 3.66 | 3.73 | 1.80 | 0 | 210.9k | 1.0B | no | 230 | 0% | 0.06 |

### horizon 1h, maker_entry

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 14.66 | 3.66 | 4.00 | 1.14 | 0 | 41.0k | 0 | yes | 28 | 0% | 0.02 |
| K1 | 13.91 | 3.66 | 3.95 | 1.71 | 0 | 50.6k | 5.0M | no | 53 | 0% | 0.03 |
| K2 | 13.16 | 3.66 | 3.75 | 1.75 | 0 | 114.6k | 10.0M | no | 122 | 0% | 0.05 |
| K3 | 11.66 | 3.66 | 3.38 | 1.92 | 0 | 478.3k | 25.0M | no | 560 | 0% | 0.10 |
| K4 | 10.66 | 3.66 | 3.12 | 2.05 | 0 | 1.2M | 50.0M | no | 1.4k | 1% | 0.17 |
| K5 | 9.66 | 3.66 | 2.88 | 2.18 | 1 | 2.6M | 100.0M | no | 3.5k | 1% | 0.27 |
| K6 | 9.11 | 3.66 | 2.75 | 2.30 | 1 | 3.9M | 250.0M | no | 5.4k | 2% | 0.34 |
| K7 | 8.41 | 3.66 | 2.58 | 2.40 | 1 | 6.5M | 1.0B | no | 9.5k | 4% | 0.47 |

### horizon 1h, maker_both

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 9.00 | 3.66 | 2.70 | 2.24 | 1 | 4.5M | 0 | yes | 6.1k | 2% | 0.36 |
| K1 | 8.50 | 3.66 | 2.60 | 2.40 | 1 | 6.0M | 5.0M | yes | 8.8k | 4% | 0.45 |
| K2 | 8.00 | 3.66 | 2.48 | 2.47 | 2 | 8.6M | 10.0M | no | 13.0k | 5% | 0.55 |
| K3 | 7.00 | 3.66 | 2.23 | 2.63 | 4 | 16.9M | 25.0M | no | 27.0k | 11% | 0.82 |
| K4 | 6.00 | 3.66 | 1.98 | 2.79 | 7 | 31.3M | 50.0M | no | 53.1k | 21% | 1.19 |
| K5 | 5.00 | 3.66 | 1.75 | 3.05 | 12 | 51.9M | 100.0M | no | 96.5k | 39% | 1.68 |
| K6 | 4.40 | 3.66 | 1.60 | 3.17 | 16 | 71.0M | 250.0M | no | 136.9k | 55% | 2.03 |
| K7 | 3.80 | 3.66 | 1.45 | 3.29 | 21 | 95.3M | 1.0B | no | 190.8k | 76% | 2.45 |


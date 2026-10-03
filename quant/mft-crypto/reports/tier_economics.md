# Économie des paliers de frais — livre MFT

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
> Barème `kraken_futures` (2025-snapshot, vérifié=False). Hypothèses : 10 symboles, breadth effective 4.0, vol annuelle 70%, spread moyen 3.0 bps, levier brut 3.0x, taux de fill passif 60%, sélection adverse 2.5 bps par jambe passive (mesurée sur fills réels Kraken), ADV 30.0M$, coefficient d'impact 0.2.

## 1. IC combiné minimal (break-even à k=1) par horizon et palier

| horizon | σ_h (bps) | K0 taker/taker | K0 maker/taker | K3 taker/taker | K3 maker/taker | K6 taker/taker | K6 maker/taker | K7 taker/taker | K7 maker/taker |
|---|---|---|---|---|---|---|---|---|---|
| 1m | 9.7 | 0.883 | 0.747 | 0.543 | 0.509 | 0.373 | 0.373 | 0.340 | 0.340 |
| 5m | 21.6 | 0.395 | 0.334 | 0.243 | 0.228 | 0.167 | 0.167 | 0.152 | 0.152 |
| 15m | 37.4 | 0.228 | 0.193 | 0.140 | 0.132 | 0.096 | 0.096 | 0.088 | 0.088 |
| 1h | 74.8 | 0.114 | 0.096 | 0.070 | 0.066 | 0.048 | 0.048 | 0.044 | 0.044 |

## 2. IC combiné requis pour un Sharpe net ≥ 2 (au palier que le livre atteint seul)

| capital | horizon | taker | maker_entry | maker_both |
|---|---|---|---|---|
| 100.0k | 5m | 0.207 (K2) | 0.169 (K3) | 0.122 (K3) |
| 100.0k | 15m | 0.135 (K3) | 0.115 (K3) | 0.083 (K4) |
| 100.0k | 1h | 0.088 (K4) | 0.078 (K4) | 0.063 (K4) |
| 250.0k | 5m | 0.230 (K5) | 0.176 (K4) | 0.110 (K5) |
| 250.0k | 15m | 0.149 (K4) | 0.118 (K5) | 0.078 (K5) |
| 250.0k | 1h | 0.095 (K5) | 0.082 (K5) | 0.059 (K6) |
| 1.0M | 5m | 0.305 (K5) | 0.209 (K5) | 0.099 (K7) |
| 1.0M | 15m | 0.199 (K5) | 0.142 (K6) | 0.068 (K7) |
| 1.0M | 1h | 0.129 (K6) | 0.099 (K6) | 0.054 (K7) |

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
| 15m | 0.08 | maker_both | K0 → K2 → K4 → K5 | K5 | 60.3k | 2.16 | K7 | 142.1k | 3.48 | 29 / 6.2k | 0 |
| 1h | 0.03 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.03 | maker_entry | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.03 | maker_both | K0 | K0 | 12 | 0.01 | K0 | 12 | 0.01 | 0 / 0 | -0 |
| 1h | 0.05 | taker | K0 | K0 | 0 | 0.00 | — | — | — | — | — |
| 1h | 0.05 | maker_entry | K0 | K0 | 28 | 0.02 | K1 | 122 | 0.05 | 27 / 1 | 0 |
| 1h | 0.05 | maker_both | K0 → K2 → K4 → K5 | K5 | 53.1k | 1.19 | K5 | 53.1k | 1.19 | 20 / 1.9k | 0 |
| 1h | 0.08 | taker | K0 → K1 | K1 | 1.8k | 0.23 | K2 | 5.9k | 0.43 | 11 / 51 | 0 |
| 1h | 0.08 | maker_entry | K0 → K2 → K4 → K5 | K5 | 81.4k | 1.88 | K5 | 81.4k | 1.88 | 21 / 3.1k | 0 |
| 1h | 0.08 | maker_both | K0 → K5 → K6 → K7 | K7 | 426.8k | 4.77 | K7 | 426.8k | 4.77 | 24 / 22.9k | 0 |

## 4. Tables complètes : PnL à chaque palier (capital 250.0k$, IC 0,05)

### horizon 5m, taker

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 20.33 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 18.33 | 3.66 | inf | 0.00 | 0 | 0 | 100.0k | no | 0 | 0% | 0.00 |
| K2 | 16.33 | 3.66 | inf | 0.00 | 0 | 0 | 1.0M | no | 0 | 0% | 0.00 |
| K3 | 15.33 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K4 | 14.33 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K5 | 13.33 | 3.66 | inf | 0.00 | 0 | 0 | 20.0M | no | 0 | 0% | 0.00 |
| K6 | 12.83 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K7 | 12.33 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |

### horizon 5m, maker_entry

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 14.66 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 13.16 | 3.66 | inf | 0.00 | 0 | 0 | 100.0k | no | 0 | 0% | 0.00 |
| K2 | 11.91 | 3.66 | inf | 0.00 | 0 | 0 | 1.0M | no | 0 | 0% | 0.00 |
| K3 | 11.16 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K4 | 10.41 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K5 | 9.66 | 3.66 | inf | 0.00 | 0 | 0 | 20.0M | no | 0 | 0% | 0.00 |
| K6 | 9.16 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K7 | 8.66 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |

### horizon 5m, maker_both

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 9.00 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 8.00 | 3.66 | inf | 0.00 | 0 | 0 | 100.0k | no | 0 | 0% | 0.00 |
| K2 | 7.50 | 3.66 | inf | 0.00 | 0 | 0 | 1.0M | no | 0 | 0% | 0.00 |
| K3 | 7.00 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K4 | 6.50 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K5 | 6.00 | 3.66 | inf | 0.00 | 0 | 0 | 20.0M | no | 0 | 0% | 0.00 |
| K6 | 5.50 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K7 | 5.00 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |

### horizon 15m, taker

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 20.33 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 18.33 | 3.66 | inf | 0.00 | 0 | 0 | 100.0k | no | 0 | 0% | 0.00 |
| K2 | 16.33 | 3.66 | inf | 0.00 | 0 | 0 | 1.0M | no | 0 | 0% | 0.00 |
| K3 | 15.33 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K4 | 14.33 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K5 | 13.33 | 3.66 | inf | 0.00 | 0 | 0 | 20.0M | no | 0 | 0% | 0.00 |
| K6 | 12.83 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K7 | 12.33 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |

### horizon 15m, maker_entry

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 14.66 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 13.16 | 3.66 | inf | 0.00 | 0 | 0 | 100.0k | no | 0 | 0% | 0.00 |
| K2 | 11.91 | 3.66 | inf | 0.00 | 0 | 0 | 1.0M | no | 0 | 0% | 0.00 |
| K3 | 11.16 | 3.66 | inf | 0.00 | 0 | 0 | 5.0M | no | 0 | 0% | 0.00 |
| K4 | 10.41 | 3.66 | inf | 0.00 | 0 | 0 | 10.0M | no | 0 | 0% | 0.00 |
| K5 | 9.66 | 3.66 | inf | 0.00 | 0 | 0 | 20.0M | no | 0 | 0% | 0.00 |
| K6 | 9.16 | 3.66 | inf | 0.00 | 0 | 0 | 50.0M | no | 0 | 0% | 0.00 |
| K7 | 8.66 | 3.66 | inf | 0.00 | 0 | 0 | 100.0M | no | 0 | 0% | 0.00 |

### horizon 15m, maker_both

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 9.00 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 8.00 | 3.66 | inf | 0.00 | 0 | 0 | 100.0k | no | 0 | 0% | 0.00 |
| K2 | 7.50 | 3.66 | 4.00 | 0.40 | 0 | 164.2k | 1.0M | no | 40 | 0% | 0.02 |
| K3 | 7.00 | 3.66 | 3.98 | 0.86 | 0 | 182.4k | 5.0M | no | 95 | 0% | 0.06 |
| K4 | 6.50 | 3.66 | 3.73 | 0.91 | 0 | 506.3k | 10.0M | no | 281 | 0% | 0.10 |
| K5 | 6.00 | 3.66 | 3.48 | 0.97 | 0 | 1.3M | 20.0M | no | 781 | 0% | 0.17 |
| K6 | 5.50 | 3.66 | 3.20 | 0.99 | 1 | 3.6M | 50.0M | no | 2.1k | 1% | 0.28 |
| K7 | 5.00 | 3.66 | 2.95 | 1.05 | 2 | 8.2M | 100.0M | no | 5.3k | 2% | 0.46 |

### horizon 1h, taker

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 20.33 | 3.66 | inf | 0.00 | 0 | 0 | 0 | yes | 0 | 0% | 0.00 |
| K1 | 18.33 | 3.66 | inf | 0.00 | 0 | 0 | 100.0k | no | 0 | 0% | 0.00 |
| K2 | 16.33 | 3.66 | inf | 0.00 | 0 | 0 | 1.0M | no | 0 | 0% | 0.00 |
| K3 | 15.33 | 3.66 | 4.00 | 0.47 | 0 | 68.4k | 5.0M | no | 20 | 0% | 0.01 |
| K4 | 14.33 | 3.66 | 4.00 | 1.47 | 0 | 68.4k | 10.0M | no | 61 | 0% | 0.03 |
| K5 | 13.33 | 3.66 | 3.80 | 1.76 | 0 | 156.3k | 20.0M | no | 168 | 0% | 0.05 |
| K6 | 12.83 | 3.66 | 3.68 | 1.82 | 0 | 256.9k | 50.0M | no | 284 | 0% | 0.07 |
| K7 | 12.33 | 3.66 | 3.55 | 1.88 | 0 | 416.0k | 100.0M | no | 475 | 0% | 0.09 |

### horizon 1h, maker_entry

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 **←** | 14.66 | 3.66 | 4.00 | 1.14 | 0 | 41.0k | 0 | yes | 28 | 0% | 0.02 |
| K1 | 13.16 | 3.66 | 3.75 | 1.75 | 0 | 114.6k | 100.0k | yes | 122 | 0% | 0.05 |
| K2 | 11.91 | 3.66 | 3.45 | 1.94 | 0 | 363.3k | 1.0M | no | 428 | 0% | 0.09 |
| K3 | 11.16 | 3.66 | 3.25 | 1.99 | 0 | 747.8k | 5.0M | no | 903 | 0% | 0.13 |
| K4 | 10.41 | 3.66 | 3.08 | 2.12 | 0 | 1.4M | 10.0M | no | 1.8k | 1% | 0.19 |
| K5 | 9.66 | 3.66 | 2.88 | 2.18 | 1 | 2.6M | 20.0M | no | 3.5k | 1% | 0.27 |
| K6 | 9.16 | 3.66 | 2.75 | 2.25 | 1 | 3.9M | 50.0M | no | 5.3k | 2% | 0.34 |
| K7 | 8.66 | 3.66 | 2.62 | 2.32 | 1 | 5.6M | 100.0M | no | 7.9k | 3% | 0.42 |

### horizon 1h, maker_both

| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 | 9.00 | 3.66 | 2.70 | 2.24 | 1 | 4.5M | 0 | yes | 6.1k | 2% | 0.36 |
| K1 | 8.00 | 3.66 | 2.48 | 2.47 | 2 | 8.6M | 100.0k | yes | 13.0k | 5% | 0.55 |
| K2 | 7.50 | 3.66 | 2.35 | 2.55 | 3 | 12.2M | 1.0M | yes | 18.8k | 8% | 0.68 |
| K3 | 7.00 | 3.66 | 2.23 | 2.63 | 4 | 16.9M | 5.0M | yes | 27.0k | 11% | 0.82 |
| K4 | 6.50 | 3.66 | 2.10 | 2.71 | 5 | 23.2M | 10.0M | yes | 38.1k | 15% | 0.99 |
| K5 **←** | 6.00 | 3.66 | 1.98 | 2.79 | 7 | 31.3M | 20.0M | yes | 53.1k | 21% | 1.19 |
| K6 | 5.50 | 3.66 | 1.85 | 2.88 | 9 | 41.7M | 50.0M | no | 73.0k | 29% | 1.42 |
| K7 | 5.00 | 3.66 | 1.75 | 3.05 | 12 | 51.9M | 100.0M | no | 96.5k | 39% | 1.68 |


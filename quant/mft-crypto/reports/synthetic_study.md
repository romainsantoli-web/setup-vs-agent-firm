# Étude synthétique — banc de test du pipeline

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
> Marché SYNTHÉTIQUE : ces chiffres valident le pipeline (il retrouve ce qui est planté, il ne trouve rien et perd de l'argent quand rien n'est planté). Ce ne sont PAS des prévisions de performance sur marché réel.

Config : 6 symboles, 60 jours, barres 1 min, horizon de trading h=15 barres, fenêtre d'entraînement 20 j, seuils k_in=2.0 / k_out=0.3, sélection adverse = demi-spread.

## Marché PLANTÉ

### Signaux (IC poolé, t journalier, verdict pré-enregistré)

| signal | h | ic | t | ic_h1 | ic_h2 | event_n | event_t | verdict |
|---|---|---|---|---|---|---|---|---|
| lead_lag | 1 | 0.0494 | 16.6741 | 0.0493 | 0.0495 | nan | nan | KEEP |
| lead_lag | 5 | 0.0202 | 15.5734 | 0.0193 | 0.0211 | nan | nan | KEEP |
| lead_lag | 15 | 0.0113 | 13.4227 | 0.0107 | 0.0120 | nan | nan | KEEP |
| lead_lag | 60 | 0.0056 | 12.8220 | 0.0051 | 0.0062 | nan | nan | WEAK |
| btc_lead | 1 | 0.0505 | 13.9489 | 0.0488 | 0.0522 | nan | nan | KEEP |
| btc_lead | 5 | 0.0208 | 6.2822 | 0.0154 | 0.0261 | nan | nan | KEEP |
| btc_lead | 15 | 0.0116 | 3.7656 | 0.0076 | 0.0156 | nan | nan | KEEP |
| btc_lead | 60 | 0.0084 | 3.0627 | 0.0083 | 0.0086 | nan | nan | WEAK |
| flow_imbalance | 1 | 0.0225 | 13.5130 | 0.0213 | 0.0236 | nan | nan | KEEP |
| flow_imbalance | 5 | 0.0311 | 9.2629 | 0.0307 | 0.0316 | nan | nan | KEEP |
| flow_imbalance | 15 | 0.0426 | 7.9736 | 0.0423 | 0.0428 | nan | nan | KEEP |
| flow_imbalance | 60 | 0.0420 | 5.2805 | 0.0378 | 0.0461 | nan | nan | KEEP |
| informed_flow | 1 | 0.0247 | 15.3582 | 0.0219 | 0.0275 | nan | nan | KEEP |
| informed_flow | 5 | 0.0451 | 14.0384 | 0.0400 | 0.0501 | nan | nan | KEEP |
| informed_flow | 15 | 0.0576 | 10.7576 | 0.0481 | 0.0671 | nan | nan | KEEP |
| informed_flow | 60 | 0.0457 | 5.4451 | 0.0419 | 0.0495 | nan | nan | KEEP |
| liquidation_reversal | 1 | 0.0013 | 1.0216 | 0.0008 | 0.0018 | 10072.0000 | 2.0305 | WEAK |
| liquidation_reversal | 5 | 0.0078 | 3.0320 | 0.0072 | 0.0084 | 2119.0000 | 1.9511 | KILL |
| liquidation_reversal | 15 | 0.0126 | 2.8550 | 0.0106 | 0.0146 | 1068.0000 | 4.2329 | KEEP |
| liquidation_reversal | 60 | 0.0112 | 1.4867 | 0.0126 | 0.0098 | 953.0000 | 4.1864 | KEEP |
| short_term_reversal | 1 | -0.0331 | -10.3713 | -0.0278 | -0.0384 | nan | nan | KILL |
| short_term_reversal | 5 | -0.0185 | -3.9977 | -0.0146 | -0.0223 | nan | nan | KILL |
| short_term_reversal | 15 | -0.0145 | -2.8554 | -0.0149 | -0.0140 | nan | nan | KILL |
| short_term_reversal | 60 | -0.0169 | -3.8655 | -0.0159 | -0.0180 | nan | nan | KILL |
| momentum | 1 | 0.0082 | 3.8169 | 0.0067 | 0.0096 | nan | nan | WEAK |
| momentum | 5 | 0.0100 | 2.2849 | 0.0077 | 0.0122 | nan | nan | WEAK |
| momentum | 15 | 0.0145 | 2.0098 | 0.0109 | 0.0180 | nan | nan | WEAK |
| momentum | 60 | 0.0213 | 1.6386 | 0.0155 | 0.0271 | nan | nan | KILL |
| funding_crowding | 1 | 0.0054 | 3.5580 | 0.0031 | 0.0077 | nan | nan | WEAK |
| funding_crowding | 5 | 0.0115 | 3.7160 | 0.0067 | 0.0164 | nan | nan | KEEP |
| funding_crowding | 15 | 0.0193 | 3.5330 | 0.0114 | 0.0272 | nan | nan | KEEP |
| funding_crowding | 60 | 0.0358 | 3.2916 | 0.0202 | 0.0514 | nan | nan | KEEP |
| premium_reversion | 1 | -0.0007 | -0.5266 | -0.0019 | 0.0005 | nan | nan | KILL |
| premium_reversion | 5 | 0.0103 | 3.4962 | 0.0068 | 0.0139 | nan | nan | KEEP |
| premium_reversion | 15 | 0.0194 | 3.9545 | 0.0126 | 0.0262 | nan | nan | KEEP |
| premium_reversion | 60 | 0.0321 | 3.5694 | 0.0218 | 0.0423 | nan | nan | KEEP |
| oi_divergence | 1 | -0.0030 | -2.4174 | -0.0040 | -0.0019 | nan | nan | KILL |
| oi_divergence | 5 | -0.0041 | -1.6248 | -0.0060 | -0.0022 | nan | nan | KILL |
| oi_divergence | 15 | -0.0051 | -1.3311 | -0.0079 | -0.0023 | nan | nan | KILL |
| oi_divergence | 60 | -0.0005 | -0.0725 | -0.0043 | 0.0034 | nan | nan | KILL |

### Combinaison walk-forward (h=15, signaux : btc_lead, flow_imbalance, funding_crowding, informed_flow, lead_lag, liquidation_reversal, premium_reversion)

IC combiné hors échantillon = **0.0737** (t=10.4, 40 jours).

| exécution | VIP0 | VIP3 | VIP6 | VIP9 |
|---|---|---|---|---|
| taker | SR -4.5 / -2.0 bps / 67 t/j | SR 3.7 / 1.6 bps / 67 t/j | SR 6.9 / 3.0 bps / 67 t/j | SR 10.7 / 4.6 bps / 67 t/j |
| maker_entry | SR 3.2 / 1.4 bps / 65 t/j | SR 9.2 / 4.0 bps / 65 t/j | SR 12.2 / 5.3 bps / 65 t/j | SR 15.3 / 6.7 bps / 65 t/j |
| maker_both | SR 9.3 / 4.1 bps / 65 t/j | SR 13.3 / 5.8 bps / 65 t/j | SR 16.0 / 7.0 bps / 65 t/j | SR 18.7 / 8.2 bps / 65 t/j |

_(170s)_

## Marché NUL (aucun effet)

### Signaux (IC poolé, t journalier, verdict pré-enregistré)

| signal | h | ic | t | ic_h1 | ic_h2 | event_n | event_t | verdict |
|---|---|---|---|---|---|---|---|---|
| lead_lag | 1 | 0.0011 | 0.6998 | 0.0016 | 0.0006 | nan | nan | KILL |
| lead_lag | 5 | -0.0026 | -1.5399 | -0.0008 | -0.0045 | nan | nan | KILL |
| lead_lag | 15 | 0.0010 | 0.6831 | 0.0022 | -0.0002 | nan | nan | KILL |
| lead_lag | 60 | 0.0003 | 0.1915 | 0.0017 | -0.0011 | nan | nan | KILL |
| btc_lead | 1 | -0.0022 | -0.6474 | 0.0005 | -0.0049 | nan | nan | KILL |
| btc_lead | 5 | -0.0007 | -0.2254 | -0.0039 | 0.0025 | nan | nan | KILL |
| btc_lead | 15 | 0.0002 | 0.0685 | -0.0024 | 0.0028 | nan | nan | KILL |
| btc_lead | 60 | 0.0035 | 1.4658 | 0.0047 | 0.0023 | nan | nan | KILL |
| flow_imbalance | 1 | -0.0013 | -0.8584 | -0.0006 | -0.0020 | nan | nan | KILL |
| flow_imbalance | 5 | -0.0008 | -0.2505 | 0.0021 | -0.0038 | nan | nan | KILL |
| flow_imbalance | 15 | 0.0041 | 0.7493 | 0.0101 | -0.0019 | nan | nan | KILL |
| flow_imbalance | 60 | 0.0120 | 1.7903 | 0.0108 | 0.0131 | nan | nan | KILL |
| informed_flow | 1 | 0.0012 | 0.9091 | -0.0008 | 0.0033 | nan | nan | KILL |
| informed_flow | 5 | 0.0013 | 0.4224 | -0.0019 | 0.0045 | nan | nan | KILL |
| informed_flow | 15 | -0.0008 | -0.1654 | -0.0072 | 0.0057 | nan | nan | KILL |
| informed_flow | 60 | -0.0052 | -0.9445 | -0.0063 | -0.0041 | nan | nan | KILL |
| liquidation_reversal | 1 | -0.0002 | -0.1526 | -0.0012 | 0.0009 | 10072.0000 | 1.4305 | KILL |
| liquidation_reversal | 5 | 0.0007 | 0.3106 | -0.0010 | 0.0024 | 2119.0000 | 1.3539 | KILL |
| liquidation_reversal | 15 | 0.0003 | 0.0810 | -0.0037 | 0.0043 | 1068.0000 | 2.4951 | WEAK |
| liquidation_reversal | 60 | -0.0071 | -1.1683 | -0.0102 | -0.0039 | 953.0000 | 0.5696 | KILL |
| short_term_reversal | 1 | -0.0005 | -0.1792 | 0.0023 | -0.0034 | nan | nan | KILL |
| short_term_reversal | 5 | -0.0024 | -0.5237 | 0.0001 | -0.0048 | nan | nan | KILL |
| short_term_reversal | 15 | -0.0030 | -0.6012 | -0.0050 | -0.0009 | nan | nan | KILL |
| short_term_reversal | 60 | -0.0095 | -2.2535 | -0.0104 | -0.0086 | nan | nan | KILL |
| momentum | 1 | 0.0017 | 0.8792 | 0.0011 | 0.0024 | nan | nan | KILL |
| momentum | 5 | 0.0042 | 0.9977 | 0.0033 | 0.0051 | nan | nan | KILL |
| momentum | 15 | 0.0074 | 1.0536 | 0.0061 | 0.0086 | nan | nan | KILL |
| momentum | 60 | 0.0114 | 0.8921 | 0.0091 | 0.0137 | nan | nan | KILL |
| funding_crowding | 1 | -0.0012 | -0.9054 | -0.0023 | -0.0002 | nan | nan | KILL |
| funding_crowding | 5 | -0.0023 | -0.8004 | -0.0048 | 0.0002 | nan | nan | KILL |
| funding_crowding | 15 | -0.0043 | -0.8275 | -0.0081 | -0.0005 | nan | nan | KILL |
| funding_crowding | 60 | -0.0095 | -0.9155 | -0.0178 | -0.0013 | nan | nan | KILL |
| premium_reversion | 1 | -0.0004 | -0.3161 | -0.0014 | 0.0006 | nan | nan | KILL |
| premium_reversion | 5 | -0.0017 | -0.6245 | -0.0038 | 0.0004 | nan | nan | KILL |
| premium_reversion | 15 | -0.0028 | -0.6106 | -0.0073 | 0.0017 | nan | nan | KILL |
| premium_reversion | 60 | -0.0015 | -0.1839 | -0.0097 | 0.0067 | nan | nan | KILL |
| oi_divergence | 1 | -0.0012 | -0.9466 | -0.0026 | 0.0003 | nan | nan | KILL |
| oi_divergence | 5 | -0.0019 | -0.7028 | -0.0058 | 0.0021 | nan | nan | KILL |
| oi_divergence | 15 | -0.0017 | -0.4088 | -0.0072 | 0.0039 | nan | nan | KILL |
| oi_divergence | 60 | 0.0004 | 0.0612 | -0.0079 | 0.0087 | nan | nan | KILL |

Aucun signal retenu à h=15 : pas de livre. (Résultat attendu sur le marché nul.)


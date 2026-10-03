"""End-to-end research study on the synthetic bench (planted + null) -> markdown report.

    python scripts/run_study.py --n-days 60 --n-symbols 6 --out reports/synthetic_study.md

The same functions (mft.study) run unchanged on real bars once data is collected.
⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from mft.fees import BINANCE_UM  # noqa: E402
from mft.models import BacktestConfig, StudyConfig  # noqa: E402
from mft.study import backtest_book, combined_forecast, panel_label, signal_report  # noqa: E402
from mft.synthetic import generate_market  # noqa: E402
from mft.validation import daily_ic, ic_summary  # noqa: E402

EXECUTIONS = ("taker", "maker_entry", "maker_both")
TIERS = ("VIP0", "VIP3", "VIP6", "VIP9")


def _md(df: pd.DataFrame, floatfmt: str = ".4f") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(format(v, floatfmt) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(out)


def study(cfg: StudyConfig, h: int, train_days: int) -> list[str]:
    lines = []
    for planted in (True, False):
        tag = "PLANTÉ" if planted else "NUL (aucun effet)"
        t0 = time.time()
        m = generate_market(cfg.model_copy(update={"planted": planted}))
        rep, corr = signal_report(m, cfg.horizons)
        lines += [f"## Marché {tag}", "", "### Signaux (IC poolé, t journalier, verdict pré-enregistré)", "",
                  _md(rep[["signal", "h", "ic", "t", "ic_h1", "ic_h2", "event_n", "event_t", "verdict"]]), ""]
        keep = sorted(set(rep.loc[(rep.verdict == "KEEP") & (rep.h == h), "signal"]))  # WEAK -> incubation, not the book
        if not keep:
            lines += [f"Aucun signal retenu à h={h} : pas de livre. (Résultat attendu sur le marché nul.)", ""]
            continue
        fc, w = combined_forecast(m, keep, h, train_days=train_days)
        y = panel_label(m, h).reindex(fc.index)
        s = ic_summary(daily_ic(fc, y))
        lines += [f"### Combinaison walk-forward (h={h}, signaux : {', '.join(keep)})", "",
                  f"IC combiné hors échantillon = **{s['ic']:.4f}** (t={s['t']:.1f}, {s['days']} jours).", "",
                  "| exécution | " + " | ".join(TIERS) + " |", "|---|" + "---|" * len(TIERS)]
        start = fc.dropna().index.get_level_values(0).min()
        mk = {k: v.loc[start:] for k, v in m.items()}
        for ex in EXECUTIONS:
            cells = []
            for tn in TIERS:
                tier = next(t for t in BINANCE_UM.tiers if t.name == tn)
                bc = BacktestConfig(k_in=2.0, k_out=0.3, max_hold_bars=3 * h, min_hold_bars=h, execution=ex,
                                    fill_window_bars=2, bars_per_day=cfg.bars_per_day)
                r = backtest_book(mk, fc, bc, tier)
                cells.append(f"SR {r['sharpe']:.1f} / {r['net_bps_per_trade']:.1f} bps / {r['trades_per_day']:.0f} t/j")
            lines.append(f"| {ex} | " + " | ".join(cells) + " |")
        lines += ["", f"_({time.time() - t0:.0f}s)_", ""]
    return lines


def main(argv: list[str] | None = None) -> str:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n-days", type=int, default=60)
    p.add_argument("--n-symbols", type=int, default=6)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--h", type=int, default=15)
    p.add_argument("--train-days", type=int, default=20)
    p.add_argument("--out", default="reports/synthetic_study.md")
    a = p.parse_args(argv)
    cfg = StudyConfig(n_days=a.n_days, n_symbols=a.n_symbols, seed=a.seed, out_path=a.out,
                      horizons=(1, 5, 15, 60))
    head = ["# Étude synthétique — banc de test du pipeline", "",
            "> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.",
            "> Marché SYNTHÉTIQUE : ces chiffres valident le pipeline (il retrouve ce qui est planté, "
            "il ne trouve rien et perd de l'argent quand rien n'est planté). Ce ne sont PAS des "
            "prévisions de performance sur marché réel.", "",
            f"Config : {a.n_symbols} symboles, {a.n_days} jours, barres 1 min, horizon de trading h={a.h} barres, "
            f"fenêtre d'entraînement {a.train_days} j, seuils k_in=2.0 / k_out=0.3, sélection adverse = demi-spread.", ""]
    text = "\n".join(head + study(cfg, a.h, a.train_days)) + "\n"
    Path(cfg.out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(cfg.out_path).write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    print(main())

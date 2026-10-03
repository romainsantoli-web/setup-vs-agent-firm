"""Fee-tier economics of the book: PnL at every tier, and the tier the book reaches by itself.

Usage:
    python scripts/tier_economics.py --venue binance_um --out reports/tier_economics.md

All market parameters below are planning ASSUMPTIONS (vol, spread, breadth, combined IC); they
are replaced by measured values once the research runs on recorded data.
⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import BaseModel, Field, field_validator  # noqa: E402

from mft import edge_math as em  # noqa: E402
from mft.fees import get_schedule  # noqa: E402
from mft.models import _no_traversal  # noqa: E402
from mft.tiers import analytic_book, ic_required_for_sharpe  # noqa: E402


class Args(BaseModel):
    # Defaults = Kraken Futures, the execution venue (Binance perps unavailable in France).
    venue: str = Field(default="kraken_futures", pattern=r"^[a-z0-9_]{2,32}$")
    out: str = Field(default="reports/tier_economics.md", min_length=1, max_length=512)
    n_symbols: int = Field(default=10, ge=1, le=200)  # the 10 PF_ perps recorded on the VPS
    n_independent: float = Field(default=4.0, gt=0, le=200)
    annual_vol: float = Field(default=0.70, gt=0, le=5)
    spread_bps: float = Field(default=3.0, ge=0, le=50)
    # Book-level gross leverage. Kraken EEA caps a position at 10x (5x for class F contracts):
    # 3x gross over 10 slots stays far from both caps and from maintenance margin.
    gross_leverage: float = Field(default=3.0, gt=0, le=10)
    fill_rate: float = Field(default=0.6, gt=0, le=1)
    # Measured by the desk: Romain's real passive Kraken fills marked out at -2.6 to -3 bp.
    adverse_bps: float = Field(default=2.5, ge=0, le=50)
    adv_usd: float = Field(default=3e7, gt=0)  # typical Kraken PF_ alt daily volume (BTC is far deeper)
    impact_coef: float = Field(default=0.2, ge=0, le=5)

    @field_validator("out")
    @classmethod
    def _p(cls, v: str) -> str:
        return _no_traversal(v)


HORIZONS = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}
CAPITALS = (100e3, 250e3, 1e6)
DETAIL_CAPITAL = 250e3
EXECUTIONS = ("taker", "maker_entry", "maker_both")


def _fmt_usd(x: float) -> str:
    for unit, div in (("B", 1e9), ("M", 1e6), ("k", 1e3)):
        if abs(x) >= div:
            return f"{x / div:.1f}{unit}"
    return f"{x:.0f}"


def _shown(sched) -> tuple:
    tiers = list(sched.tiers[::3])
    return tuple(tiers if tiers[-1] is sched.tiers[-1] else tiers + [sched.tiers[-1]])


def breakeven_table(a: Args) -> list[str]:
    sched = get_schedule(a.venue)
    lines = ["| horizon | σ_h (bps) | " + " | ".join(f"{t.name} taker/taker | {t.name} maker/taker" for t in _shown(sched)) + " |",
             "|---|---|" + "---|---|" * len(_shown(sched))]
    for hname, hs in HORIZONS.items():
        sig = em.sigma_h_bps(a.annual_vol, hs)
        cells = []
        for t in _shown(sched):
            c_tt = 2 * t.taker_bps + a.spread_bps
            c_mt = t.maker_bps + t.taker_bps + a.spread_bps / 2 + a.adverse_bps  # taker exit + passive entry
            cells += [f"{em.breakeven_ic(sig, c_tt, 1.0):.3f}", f"{em.breakeven_ic(sig, c_mt, 1.0):.3f}"]
        lines.append(f"| {hname} | {sig:.1f} | " + " | ".join(cells) + " |")
    return lines


def book_tables(a: Args, capital: float, ic: float, horizon: str, execution: str) -> tuple[list[str], dict]:
    sched = get_schedule(a.venue)
    res = analytic_book(sched, ic=ic, horizon_s=HORIZONS[horizon], annual_vol=a.annual_vol,
                        n_symbols=a.n_symbols, n_independent=a.n_independent, capital_usd=capital,
                        gross_leverage=a.gross_leverage, execution=execution, spread_bps=a.spread_bps,
                        adverse_bps=a.adverse_bps, fill_rate=a.fill_rate, adv_usd=a.adv_usd,
                        impact_coef=a.impact_coef)
    lines = ["| tier | RT cost (bps) | impact/jambe taker | k | net edge (bps) | trades/day | volume/window | tier threshold | self-sustaining | PnL/yr | return | Sharpe |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["table"]:
        mark = " **←**" if r["tier"] == res["reached"] else ""
        lines.append(
            f"| {r['tier']}{mark} | {r['rt_cost_bps']:.2f} | {r['impact_bps_leg']:.2f} | {r['k']:.2f} | {r['net_edge_bps']:.2f} | "
            f"{r['trades_per_day']:.0f} | {_fmt_usd(r['volume_window_usd'])} | {_fmt_usd(r['tier_min_volume'])} | "
            f"{'yes' if r['self_sustaining'] else 'no'} | {_fmt_usd(r['pnl_year_usd'])} | "
            f"{100 * r['return_on_capital']:.0f}% | {r['sharpe']:.2f} |")
    return lines, res


def main(argv: list[str] | None = None) -> str:
    p = argparse.ArgumentParser(description=__doc__)
    for name, field in Args.model_fields.items():
        p.add_argument(f"--{name.replace('_', '-')}", type=type(field.default), default=field.default)
    a = Args(**vars(p.parse_args(argv)))
    sched = get_schedule(a.venue)

    out = ["# Économie des paliers de frais — livre MFT", "",
           "> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.",
           f"> Barème `{sched.venue}` ({sched.as_of}, vérifié={sched.verified}). Hypothèses : "
           f"{a.n_symbols} symboles, breadth effective {a.n_independent}, vol annuelle {a.annual_vol:.0%}, "
           f"spread moyen {a.spread_bps} bps, levier brut {a.gross_leverage}x, taux de fill passif {a.fill_rate:.0%}, "
           f"sélection adverse {a.adverse_bps} bps par jambe passive (mesurée sur fills réels Kraken), "
           f"ADV {_fmt_usd(a.adv_usd)}$, coefficient d'impact {a.impact_coef}.", "",
           "## 1. IC combiné minimal (break-even à k=1) par horizon et palier", ""]
    out += breakeven_table(a)
    kw = dict(annual_vol=a.annual_vol, n_symbols=a.n_symbols, n_independent=a.n_independent,
              gross_leverage=a.gross_leverage, spread_bps=a.spread_bps, adverse_bps=a.adverse_bps,
              fill_rate=a.fill_rate, adv_usd=a.adv_usd, impact_coef=a.impact_coef)
    req = ["", "## 2. IC combiné requis pour un Sharpe net ≥ 2 (au palier que le livre atteint seul)", "",
           "| capital | horizon | taker | maker_entry | maker_both |", "|---|---|---|---|---|"]
    for capital in CAPITALS:
        for horizon in ("5m", "15m", "1h"):
            cells = []
            for ex in EXECUTIONS:
                r = ic_required_for_sharpe(sched, 2.0, capital_usd=capital, horizon_s=HORIZONS[horizon],
                                           execution=ex, **kw)
                cells.append("n/a" if r["tier"] is None else f"{r['ic']:.3f} ({r['tier']})")
            req.append(f"| {_fmt_usd(capital)} | {horizon} | " + " | ".join(cells) + " |")
    summary = ["", f"## 3. Palier atteint et PnL — capital {_fmt_usd(DETAIL_CAPITAL)}$", "",
               "| horizon | IC combiné | exécution | chemin organique | palier atteint | PnL/an | Sharpe | meilleur palier soutenable | PnL/an | Sharpe | rampe (jours / PnL) | payback (j) |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    details: list[str] = ["", f"## 4. Tables complètes : PnL à chaque palier (capital {_fmt_usd(DETAIL_CAPITAL)}$, IC 0,05)", ""]
    for horizon in ("5m", "15m", "1h"):
        for ic in (0.03, 0.05, 0.08):
            for ex in EXECUTIONS:
                lines, res = book_tables(a, DETAIL_CAPITAL, ic, horizon, ex)
                row = next(r for r in res["table"] if r["tier"] == res["reached"])
                b = res["bootstrap"]
                if b is None:
                    boot_cells = "— | — | — | — | —"
                else:
                    br = next(r for r in res["table"] if r["tier"] == b["tier"])
                    boot_cells = (f"{b['tier']} | {_fmt_usd(br['pnl_year_usd'])} | {br['sharpe']:.2f} | "
                                  f"{b['days']:.0f} / {_fmt_usd(b['ramp_pnl_usd'])} | {b['payback_days']:.0f}")
                summary.append(f"| {horizon} | {ic} | {ex} | {' → '.join(res['path'])} | "
                               f"{res['reached']} | {_fmt_usd(row['pnl_year_usd'])} | {row['sharpe']:.2f} | {boot_cells} |")
                if ic == 0.05:
                    details += [f"### horizon {horizon}, {ex}", ""] + lines + [""]
    out += req
    text = "\n".join(out + summary + details) + "\n"
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    print(main())

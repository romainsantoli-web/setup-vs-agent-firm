"""Bar-level execution simulator for a single perp, with honest costs.

Decision at the close of bar t using a forecast known at t. Fills happen no earlier than bar t+1
for passive orders, and at close_t +/- half-spread (+ impact) for taker orders — i.e. we assume
our 15 ms reaction is enough to cross at the prevailing touch, never better.

Passive fill rule (conservative, encodes adverse selection): a resting buy at price L fills
during a later bar only if that bar's low trades *strictly through* L. Being filled therefore
means the price moved against us; being right means we often miss. Unfilled orders are
cancelled or, if `chase_unfilled`, converted to a taker order when the signal is still alive.

Each passive fill is then charged `adverse_bps` (default = half-spread): the bar model cannot
see queue position, so selection is imposed explicitly instead of hoping the data reveals it.

Accounting is cash + units * mark, so every cost (fees, spread, impact, funding) is explicit.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .models import BacktestConfig, CostParams, FeeTier


@dataclass
class BacktestResult:
    equity: pd.Series
    trades: pd.DataFrame
    volume_usd: float
    fees_usd: float
    funding_usd: float
    maker_fill_rate: float
    n_days: float

    @property
    def daily_pnl(self) -> pd.Series:
        return self.equity.resample("1D").last().diff().fillna(self.equity.resample("1D").last().iloc[0])

    @property
    def volume_per_day(self) -> float:
        return self.volume_usd / max(self.n_days, 1e-9)


def impact_bps(cost: CostParams, notional: float) -> float:
    return cost.impact_coef * cost.daily_vol_bps * np.sqrt(notional / cost.adv_usd)


def run_backtest(df: pd.DataFrame, forecast: pd.Series, cfg: BacktestConfig, fees: FeeTier,
                 cost: CostParams) -> BacktestResult:
    close = df["close"].to_numpy(float)
    high = df["high"].to_numpy(float)
    low = df["low"].to_numpy(float)
    hs = (df["spread_bps"].to_numpy(float) / 2.0) if "spread_bps" in df else np.full(len(df), cost.half_spread_bps)
    fund = df["funding_rate_bps"].to_numpy(float) if "funding_rate_bps" in df else np.zeros(len(df))
    is_fund = df["is_funding"].to_numpy(bool) if "is_funding" in df else np.zeros(len(df), bool)
    z = forecast.reindex(df.index).to_numpy(float)
    n = len(df)
    imp = impact_bps(cost, cfg.notional_usd) / 1e4
    adverse = (hs if cost.adverse_bps is None else np.full(n, cost.adverse_bps)) / 1e4

    cash = 0.0
    units = 0.0
    pos = 0  # -1, 0, +1
    entry_i = -1
    pending: tuple[int, float, int, str] | None = None  # (side, limit, expiry, purpose)
    vol_usd = fees_usd = fund_usd = 0.0
    maker_tries = maker_fills = 0
    equity = np.empty(n)
    trades: list[dict] = []
    open_trade: dict | None = None

    def fill(i: int, side: int, price: float, maker: bool, purpose: str) -> None:
        nonlocal cash, units, pos, entry_i, vol_usd, fees_usd, open_trade
        qty = side * cfg.notional_usd / price if purpose == "entry" else -units
        notional = abs(qty) * price
        fee = notional * (fees.maker_bps if maker else fees.taker_bps) / 1e4
        cash -= qty * price + fee
        units += qty
        vol_usd += notional
        fees_usd += fee
        if purpose == "entry":
            pos, entry_i = side, i
            open_trade = {"entry_ts": df.index[i], "side": side, "entry_px": price,
                          "entry_maker": maker, "cash0": cash + qty * price + fee, "fees": fee}
        else:
            assert open_trade is not None
            open_trade.update({"exit_ts": df.index[i], "exit_px": price, "exit_maker": maker,
                               "fees": open_trade["fees"] + fee, "hold_bars": i - entry_i})
            open_trade["pnl"] = open_trade["side"] * (price - open_trade["entry_px"]) * abs(
                cfg.notional_usd / open_trade["entry_px"]) - open_trade["fees"]
            open_trade.pop("cash0")
            trades.append(open_trade)
            open_trade = None
            pos, entry_i, units = 0, -1, 0.0

    def taker_px(i: int, side: int) -> float:
        return close[i] * (1 + side * (hs[i] / 1e4 + imp))

    for i in range(n):
        # 1) resting passive order: can only fill on bars after placement
        if pending is not None:
            side, limit, expiry, purpose = pending
            through = (low[i] < limit) if side > 0 else (high[i] > limit)
            if through:
                maker_fills += 1
                fill(i, side, limit * (1 + side * adverse[i]), True, purpose)
                pending = None
            elif i >= expiry:
                pending = None
                alive = np.isfinite(z[i]) and side * z[i] > cfg.k_in
                if purpose == "exit" or (cfg.chase_unfilled and alive):
                    fill(i, side, taker_px(i, side), False, purpose)
        # 2) funding settlement on open position (positive rate: longs pay shorts)
        if is_fund[i] and units != 0.0:
            pay = units * close[i] * fund[i] / 1e4
            cash -= pay
            fund_usd -= pay
        # 3) decisions
        zi = z[i]
        if pending is None and np.isfinite(zi):
            if pos == 0:
                if abs(zi) > cfg.k_in:
                    side = 1 if zi > 0 else -1
                    if cfg.execution == "taker":
                        fill(i, side, taker_px(i, side), False, "entry")
                    else:
                        maker_tries += 1
                        limit = close[i] * (1 - side * (hs[i] + cfg.maker_offset_bps) / 1e4)
                        pending = (side, limit, i + cfg.fill_window_bars, "entry")
            else:
                held = i - entry_i
                flip = pos * zi < -cfg.k_in
                decay = held >= cfg.min_hold_bars and pos * zi < cfg.k_out
                if held >= cfg.max_hold_bars or flip or decay:
                    side = -pos
                    if cfg.execution == "maker_both" and not flip:
                        maker_tries += 1
                        limit = close[i] * (1 - side * (hs[i] + cfg.maker_offset_bps) / 1e4)
                        pending = (side, limit, i + cfg.fill_window_bars, "exit")
                    else:
                        fill(i, side, taker_px(i, side), False, "exit")
                        if flip:  # reverse: the opposite signal is already above the entry band
                            if cfg.execution == "taker":
                                fill(i, side, taker_px(i, side), False, "entry")
                            else:
                                maker_tries += 1
                                limit = close[i] * (1 - side * (hs[i] + cfg.maker_offset_bps) / 1e4)
                                pending = (side, limit, i + cfg.fill_window_bars, "entry")
        equity[i] = cash + units * close[i]

    eq = pd.Series(equity, index=df.index)
    n_days = (df.index[-1] - df.index[0]).total_seconds() / 86_400 if n > 1 else 0.0
    return BacktestResult(
        equity=eq, trades=pd.DataFrame(trades), volume_usd=vol_usd, fees_usd=fees_usd,
        funding_usd=fund_usd, maker_fill_rate=maker_fills / maker_tries if maker_tries else float("nan"),
        n_days=n_days,
    )


def summarize(results: dict[str, BacktestResult]) -> dict[str, float]:
    """Aggregate per-symbol results into book-level stats (daily PnL summed across symbols)."""
    daily = sum(r.daily_pnl for r in results.values())
    n_days = max(r.n_days for r in results.values())
    trades = sum(len(r.trades) for r in results.values())
    vol = sum(r.volume_usd for r in results.values())
    from .validation import sharpe_annual
    return {
        "pnl_usd": float(daily.sum()),
        "pnl_per_day": float(daily.mean()),
        "sharpe": sharpe_annual(daily),
        "trades": trades,
        "trades_per_day": trades / max(n_days, 1e-9),
        "volume_per_day": vol / max(n_days, 1e-9),
        "fees_usd": float(sum(r.fees_usd for r in results.values())),
        "funding_usd": float(sum(r.funding_usd for r in results.values())),
        "net_bps_per_trade": float(daily.sum() / (vol / 2) * 1e4) if vol else 0.0,
    }

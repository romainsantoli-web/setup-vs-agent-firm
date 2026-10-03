"""Public historical data: URL builders, downloader, and trades -> bars aggregation.

Archives (no API key):
  * Binance USDⓈ-M  https://data.binance.vision/data/futures/um/{daily|monthly}/...
      aggTrades, trades, bookTicker, metrics (OI, long/short ratios, 5 min), klines,
      premiumIndexKlines, markPriceKlines (daily) ; fundingRate (monthly).
  * Bybit           https://public.bybit.com/trading/{SYMBOL}/{SYMBOL}{YYYY-MM-DD}.csv.gz
Liquidations are NOT in these archives in usable form: Binance `!forceOrder@arr` only pushes the
largest liquidation per symbol per second, Bybit `allLiquidation` pushes all. They must be
recorded live by our own collector on the London VPS from day one (see RESEARCH.md §6).
"""

from __future__ import annotations

import datetime as dt
import io
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from .models import DownloadRequest

BINANCE_UM_BASE = "https://data.binance.vision/data/futures/um"
BYBIT_BASE = "https://public.bybit.com/trading"
_MONTHLY_ONLY = {"fundingRate"}
_WITH_INTERVAL = {"klines", "premiumIndexKlines"}


def _dates(start: dt.date, end: dt.date) -> list[dt.date]:
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]


def build_urls(req: DownloadRequest) -> list[str]:
    if req.venue == "bybit":
        if req.dataset != "trades":
            raise ValueError("bybit public archive only provides 'trades'")
        return [f"{BYBIT_BASE}/{req.symbol}/{req.symbol}{d.isoformat()}.csv.gz" for d in _dates(req.start, req.end)]
    if req.dataset in _MONTHLY_ONLY:
        months = sorted({(d.year, d.month) for d in _dates(req.start, req.end)})
        return [f"{BINANCE_UM_BASE}/monthly/{req.dataset}/{req.symbol}/{req.symbol}-{req.dataset}-{y:04d}-{m:02d}.zip"
                for y, m in months]
    urls = []
    for d in _dates(req.start, req.end):
        if req.dataset in _WITH_INTERVAL:
            urls.append(f"{BINANCE_UM_BASE}/daily/{req.dataset}/{req.symbol}/{req.interval}/"
                        f"{req.symbol}-{req.interval}-{d.isoformat()}.zip")
        else:
            urls.append(f"{BINANCE_UM_BASE}/daily/{req.dataset}/{req.symbol}/{req.symbol}-{req.dataset}-{d.isoformat()}.zip")
    return urls


def download(req: DownloadRequest, retries: int = 4, opener=urllib.request.urlopen) -> list[Path]:
    """Fetch every archive for the request into out_dir (skips files already present)."""
    out = Path(req.out_dir) / req.venue / req.dataset / req.symbol
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for url in build_urls(req):
        dest = out / url.rsplit("/", 1)[1]
        if dest.exists() and dest.stat().st_size > 0:
            saved.append(dest)
            continue
        for attempt in range(retries):
            try:
                with opener(url, timeout=60) as resp:
                    dest.write_bytes(resp.read())
                saved.append(dest)
                break
            except Exception as exc:  # noqa: BLE001 — network errors vary by platform
                if getattr(exc, "code", None) == 404:
                    break  # day not published (listing date, outage): skip, do not retry
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** (attempt + 1))
    return saved


def read_binance_agg_trades(path: Path) -> pd.DataFrame:
    """Binance aggTrades zip -> DataFrame[ts, price, qty, buyer_is_maker]."""
    cols = ["agg_id", "price", "qty", "first_id", "last_id", "transact_time", "is_buyer_maker"]
    with zipfile.ZipFile(path) as z:
        raw = z.read(z.namelist()[0])
    first = raw.split(b"\n", 1)[0]
    header = 0 if first.startswith(b"agg_trade_id") else None
    df = pd.read_csv(io.BytesIO(raw), header=header, names=None if header == 0 else cols)
    df.columns = cols
    return pd.DataFrame({
        "ts": pd.to_datetime(df["transact_time"], unit="ms", utc=True),
        "price": df["price"].astype(float), "qty": df["qty"].astype(float),
        "buyer_is_maker": df["is_buyer_maker"].astype(str).str.lower().isin(["true", "1"]),
    })


def trades_to_bars(trades: pd.DataFrame, bar: str = "1min", large_usd: float = 100_000.0) -> pd.DataFrame:
    """Aggregate prints into bars with aggressor-signed and size-split volumes.

    `buyer_is_maker=True` means the aggressor SOLD. `large_usd` must be a fixed, pre-set
    threshold (a full-sample quantile would leak the future).
    """
    t = trades.copy()
    t["usd"] = t["price"] * t["qty"]
    buy = ~t["buyer_is_maker"]
    big = t["usd"] >= large_usd
    t["buy_volume"] = np.where(buy, t["usd"], 0.0)
    t["sell_volume"] = np.where(~buy, t["usd"], 0.0)
    t["large_buy_volume"] = np.where(buy & big, t["usd"], 0.0)
    t["large_sell_volume"] = np.where(~buy & big, t["usd"], 0.0)
    g = t.set_index("ts").resample(bar, label="right", closed="right")
    bars = g["price"].ohlc()
    for c in ["usd", "buy_volume", "sell_volume", "large_buy_volume", "large_sell_volume"]:
        bars[c] = g[c].sum()
    bars["n_trades"] = g["price"].count()
    bars = bars.rename(columns={"usd": "volume"})
    bars["close"] = bars["close"].ffill()
    for c in ["open", "high", "low"]:
        bars[c] = bars[c].fillna(bars["close"])
    return bars

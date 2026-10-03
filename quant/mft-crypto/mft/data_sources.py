"""Public historical data: URL builders, downloader, and trades -> bars aggregation.

Archives (no API key):
  * Binance USDⓈ-M  https://data.binance.vision/data/futures/um/{daily|monthly}/...
      aggTrades, trades, bookTicker, metrics (OI, long/short ratios, 5 min), klines,
      premiumIndexKlines, markPriceKlines (daily) ; fundingRate (monthly).
  * Bybit           https://public.bybit.com/trading/{SYMBOL}/{SYMBOL}{YYYY-MM-DD}.csv.gz
  * Kraken Futures  (EXECUTION VENUE) public REST, JSON:
      candles    https://futures.kraken.com/api/charts/v1/{trade|mark|spot}/{PF_XBTUSD}/1m?from=&to=  (s)
      executions https://futures.kraken.com/api/history/v2/market/{PF_XBTUSD}/executions?since=&before= (ms,
                 paginated with `continuationToken`)
      funding    https://futures.kraken.com/derivatives/api/v4/historicalfundingrates?symbol=PF_XBTUSD
    Endpoint shapes are from the public docs as known to the author: VERIFY on first download.
Liquidations are NOT in these archives in usable form: Binance `!forceOrder@arr` only pushes the
largest liquidation per symbol per second, Bybit `allLiquidation` pushes all. They must be
recorded live by our own collector on the London VPS from day one (see RESEARCH.md §6).
"""

from __future__ import annotations

import datetime as dt
import io
import json
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from .models import DownloadRequest

BINANCE_UM_BASE = "https://data.binance.vision/data/futures/um"
BYBIT_BASE = "https://public.bybit.com/trading"
KRAKEN_FUT_BASE = "https://futures.kraken.com"
_MONTHLY_ONLY = {"fundingRate"}
_WITH_INTERVAL = {"klines", "premiumIndexKlines"}


def _dates(start: dt.date, end: dt.date) -> list[dt.date]:
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]


def _day_bounds(d: dt.date) -> tuple[int, int]:
    start = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
    return start, start + 86_400


def build_urls(req: DownloadRequest) -> list[str]:
    if req.venue == "kraken_futures":
        if req.dataset == "funding":
            return [f"{KRAKEN_FUT_BASE}/derivatives/api/v4/historicalfundingrates?symbol={req.symbol}"]
        urls = []
        for d in _dates(req.start, req.end):
            a, b = _day_bounds(d)
            if req.dataset == "candles":
                for tick in ("trade", "mark", "spot"):
                    urls.append(f"{KRAKEN_FUT_BASE}/api/charts/v1/{tick}/{req.symbol}/{req.interval}?from={a}&to={b}")
            elif req.dataset == "executions":
                urls.append(f"{KRAKEN_FUT_BASE}/api/history/v2/market/{req.symbol}/executions"
                            f"?since={a * 1000}&before={b * 1000}&sort=asc")
            else:
                raise ValueError("kraken_futures datasets: candles, executions, funding")
        return urls
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
        dest = out / _filename(url)
        if dest.exists() and dest.stat().st_size > 0:
            saved.append(dest)
            continue
        for attempt in range(retries):
            try:
                if "futures.kraken.com" in url and "/executions" in url:
                    dest.write_text(json.dumps(fetch_kraken_executions(url, opener)), encoding="utf-8")
                else:
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


def _filename(url: str) -> str:
    """Stable local file name; Kraken URLs carry their identity in the path + query string."""
    if "futures.kraken.com" not in url:
        return url.rsplit("/", 1)[1]
    tail = url.split("futures.kraken.com/", 1)[1]
    return tail.replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "-") + ".json"


def fetch_kraken_executions(url: str, opener=urllib.request.urlopen, max_pages: int = 10_000) -> list[dict]:
    """Follow Kraken's `continuationToken` pagination for one executions URL."""
    out: list[dict] = []
    token = None
    for _ in range(max_pages):
        page_url = url + (f"&continuationToken={token}" if token else "")
        with opener(page_url, timeout=60) as resp:
            page = json.loads(resp.read())
        out += page.get("elements", [])
        token = page.get("continuationToken")
        if not token:
            break
    return out


def read_kraken_executions(elements: list[dict]) -> pd.DataFrame:
    """Kraken Futures public executions -> DataFrame[ts, price, qty, buyer_is_maker]."""
    rows = []
    for el in elements:
        ex = el["event"]["Execution"]["execution"]
        taker_sells = ex["takerOrder"]["direction"].lower() == "sell"
        rows.append({"ts": pd.to_datetime(ex["timestamp"], unit="ms", utc=True), "price": float(ex["price"]),
                     "qty": float(ex["quantity"]), "buyer_is_maker": taker_sells})
    return pd.DataFrame(rows, columns=["ts", "price", "qty", "buyer_is_maker"])


def read_kraken_candles(payload: dict) -> pd.DataFrame:
    c = pd.DataFrame(payload.get("candles", []))
    if c.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    c.index = pd.to_datetime(c.pop("time"), unit="ms", utc=True)
    return c[["open", "high", "low", "close", "volume"]].astype(float)


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

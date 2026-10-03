"""Live market-data collector for the London VPS (public streams, no API key).

Why it exists: the data we most need is the data nobody archives for us —
  * every liquidation (Bybit `allLiquidation` publishes all of them; Binance `!forceOrder@arr`
    only the largest per symbol per second, still useful as a cross-check),
  * top-of-book on several venues *timestamped on our own clock* (lead-lag and our real
    latency to each venue are only measurable from where we will trade),
  * mark / index / predicted funding at 1 s.
Records are normalised to one schema and written to hourly-rotated gzip JSONL:
    {out_dir}/{venue}/{YYYY-MM-DD}/{HH}.jsonl.gz
Every record carries `ts` (exchange event time, ms) and `rx_ns` (our receive time, ns).
"""

from __future__ import annotations

import asyncio
import gzip
import json
import time
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import SYMBOL_RE, _no_traversal

BINANCE_WS = "wss://fstream.binance.com/stream?streams="
BYBIT_WS = "wss://stream.bybit.com/v5/public/linear"
# Bybit v5 docs: "When you receive a Buy update, this means that a long position has been
# liquidated". VERIFY against live data (price direction around the print) before trusting it.
BYBIT_LIQ_BUY_IS_LONG = True


class CollectorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    symbols: tuple[str, ...] = Field(min_length=1, max_length=100)
    venues: tuple[str, ...] = Field(default=("binance_um", "bybit"), min_length=1, max_length=4)
    out_dir: str = Field(default="data/live", min_length=1, max_length=512)
    flush_every: int = Field(default=500, ge=1, le=1_000_000)

    @field_validator("symbols")
    @classmethod
    def _sym(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        import re
        bad = [s for s in v if not re.match(SYMBOL_RE, s)]
        if bad:
            raise ValueError(f"invalid symbols: {bad}")
        return v

    @field_validator("venues")
    @classmethod
    def _ven(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        if set(v) - {"binance_um", "bybit"}:
            raise ValueError("supported venues: binance_um, bybit")
        return v

    @field_validator("out_dir")
    @classmethod
    def _out(cls, v: str) -> str:
        return _no_traversal(v)


# --- normalisers (pure, unit-tested) ---------------------------------------------------------

def _f(x: Any) -> float:
    return float(x)


def normalize_binance(msg: dict, rx_ns: int) -> list[dict]:
    d = msg.get("data", msg)
    e = d.get("e")
    if e == "aggTrade":
        return [{"venue": "binance_um", "type": "trade", "symbol": d["s"], "ts": d["T"], "rx_ns": rx_ns,
                 "price": _f(d["p"]), "qty": _f(d["q"]), "side": "sell" if d["m"] else "buy"}]
    if e == "bookTicker":
        return [{"venue": "binance_um", "type": "bbo", "symbol": d["s"], "ts": d.get("T", d.get("E")), "rx_ns": rx_ns,
                 "bid": _f(d["b"]), "bid_qty": _f(d["B"]), "ask": _f(d["a"]), "ask_qty": _f(d["A"])}]
    if e == "markPriceUpdate":
        return [{"venue": "binance_um", "type": "mark", "symbol": d["s"], "ts": d["E"], "rx_ns": rx_ns,
                 "mark": _f(d["p"]), "index": _f(d["i"]), "funding_rate": _f(d["r"]), "next_funding_ts": d["T"]}]
    if e == "forceOrder":
        o = d["o"]
        px, qty = _f(o["ap"]) or _f(o["p"]), _f(o["z"]) or _f(o["q"])
        # forced SELL = a long position being liquidated
        return [{"venue": "binance_um", "type": "liquidation", "symbol": o["s"], "ts": o["T"], "rx_ns": rx_ns,
                 "liq_side": "long" if o["S"] == "SELL" else "short", "price": px, "qty": qty, "usd": px * qty}]
    return []


class BybitState:
    """Bybit sends snapshots then partial deltas for tickers/orderbook: keep last full state."""

    def __init__(self) -> None:
        self.tickers: dict[str, dict] = {}
        self.books: dict[str, dict] = {}


def normalize_bybit(msg: dict, rx_ns: int, state: BybitState) -> list[dict]:
    topic = msg.get("topic", "")
    data = msg.get("data")
    if data is None:
        return []  # pong / subscription acks
    out: list[dict] = []
    if topic.startswith("publicTrade."):
        for t in data:
            out.append({"venue": "bybit", "type": "trade", "symbol": t["s"], "ts": t["T"], "rx_ns": rx_ns,
                        "price": _f(t["p"]), "qty": _f(t["v"]), "side": t["S"].lower()})
    elif topic.startswith("allLiquidation."):
        for t in data:
            is_buy = t["S"] == "Buy"
            long_liq = is_buy if BYBIT_LIQ_BUY_IS_LONG else not is_buy
            px, qty = _f(t["p"]), _f(t["v"])
            out.append({"venue": "bybit", "type": "liquidation", "symbol": t["s"], "ts": t["T"], "rx_ns": rx_ns,
                        "liq_side": "long" if long_liq else "short", "price": px, "qty": qty, "usd": px * qty})
    elif topic.startswith("orderbook.1."):
        sym = data["s"]
        book = {} if msg.get("type") == "snapshot" else dict(state.books.get(sym, {}))
        if data.get("b"):
            book["bid"], book["bid_qty"] = _f(data["b"][0][0]), _f(data["b"][0][1])
        if data.get("a"):
            book["ask"], book["ask_qty"] = _f(data["a"][0][0]), _f(data["a"][0][1])
        state.books[sym] = book
        if {"bid", "ask"} <= set(book):
            out.append({"venue": "bybit", "type": "bbo", "symbol": sym, "ts": msg.get("cts", msg.get("ts")),
                        "rx_ns": rx_ns, **book})
    elif topic.startswith("tickers."):
        sym = data["symbol"]
        cur = {} if msg.get("type") == "snapshot" else dict(state.tickers.get(sym, {}))
        cur.update(data)
        state.tickers[sym] = cur
        if all(k in cur for k in ("markPrice", "indexPrice", "fundingRate")):
            out.append({"venue": "bybit", "type": "mark", "symbol": sym, "ts": msg.get("ts"), "rx_ns": rx_ns,
                        "mark": _f(cur["markPrice"]), "index": _f(cur["indexPrice"]),
                        "funding_rate": _f(cur["fundingRate"]),
                        "next_funding_ts": int(cur.get("nextFundingTime", 0) or 0),
                        "oi_usd": _f(cur.get("openInterestValue", "nan") or "nan")})
    return out


def binance_url(symbols: Iterable[str]) -> str:
    streams = []
    for s in symbols:
        s = s.lower()
        streams += [f"{s}@aggTrade", f"{s}@bookTicker", f"{s}@markPrice@1s"]
    return BINANCE_WS + "/".join(streams + ["!forceOrder@arr"])


def bybit_subscriptions(symbols: Iterable[str]) -> list[dict]:
    args = []
    for s in symbols:
        args += [f"publicTrade.{s}", f"orderbook.1.{s}", f"tickers.{s}", f"allLiquidation.{s}"]
    # Bybit caps args per request: send in chunks of 10
    return [{"op": "subscribe", "args": args[i:i + 10]} for i in range(0, len(args), 10)]


# --- storage ---------------------------------------------------------------------------------

class HourlyWriter:
    def __init__(self, out_dir: str, venue: str, flush_every: int = 500) -> None:
        self.root = Path(out_dir) / venue
        self.flush_every = flush_every
        self._buf: list[str] = []
        self._key: str | None = None

    def _path(self, key: str) -> Path:
        day, hour = key.split("T")
        p = self.root / day / f"{hour}.jsonl.gz"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def write(self, records: list[dict]) -> None:
        for r in records:
            key = time.strftime("%Y-%m-%dT%H", time.gmtime(r["rx_ns"] / 1e9))
            if self._key is not None and key != self._key:
                self.flush()
            self._key = key
            self._buf.append(json.dumps(r, separators=(",", ":")))
        if len(self._buf) >= self.flush_every:
            self.flush()

    def flush(self) -> None:
        if not self._buf or self._key is None:
            return
        with gzip.open(self._path(self._key), "at", encoding="utf-8") as fh:
            fh.write("\n".join(self._buf) + "\n")
        self._buf.clear()


def read_records(paths: Iterable[Path]) -> pd.DataFrame:
    rows: list[dict] = []
    for p in paths:
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            rows += [json.loads(line) for line in fh if line.strip()]
    df = pd.DataFrame(rows)
    if not df.empty:
        df["time"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df


def records_to_bar_columns(rec: pd.DataFrame, symbol: str, venue: str, bar: str = "1min",
                           ref_venue: str | None = None) -> pd.DataFrame:
    """Collected records -> the bar columns the signal library expects (liquidations, spread,
    funding, premium, OI, cross-venue reference mid). Trades -> use data_sources.trades_to_bars."""
    r = rec[rec["symbol"] == symbol]
    own = r[r["venue"] == venue]
    out = pd.DataFrame()
    bbo = own[own["type"] == "bbo"].set_index("time")
    if not bbo.empty:
        mid = (bbo["bid"] + bbo["ask"]) / 2
        out["mid"] = mid.resample(bar, label="right", closed="right").last()
        out["spread_bps"] = ((bbo["ask"] - bbo["bid"]) / mid * 1e4).resample(bar, label="right", closed="right").mean()
    liq_all = r[r["type"] == "liquidation"].set_index("time")  # liquidations: all venues, market-wide flow
    for side in ("long", "short"):
        s = liq_all.loc[liq_all["liq_side"] == side, "usd"] if not liq_all.empty else pd.Series(dtype=float)
        out[f"liq_{side}_usd"] = s.resample(bar, label="right", closed="right").sum() if len(s) else 0.0
    mark = own[own["type"] == "mark"].set_index("time")
    if not mark.empty:
        g = mark.resample(bar, label="right", closed="right")
        out["funding_rate_bps"] = g["funding_rate"].last() * 1e4
        out["premium_bps"] = ((mark["mark"] / mark["index"] - 1) * 1e4).resample(bar, label="right", closed="right").mean()
        if "oi_usd" in mark:
            out["oi_usd"] = g["oi_usd"].last()
    if ref_venue:
        ref = r[(r["venue"] == ref_venue) & (r["type"] == "bbo")].set_index("time")
        if not ref.empty:
            out["close_ref"] = ((ref["bid"] + ref["ask"]) / 2).resample(bar, label="right", closed="right").last()
    for c in ("liq_long_usd", "liq_short_usd"):
        out[c] = out[c].fillna(0.0)
    return out.ffill()


# --- runner ----------------------------------------------------------------------------------

Connect = Callable[[str], Awaitable[Any]]


async def run_stream(url: str, on_message: Callable[[dict, int], None], connect: Connect,
                     subscribe: list[dict] | None = None, max_sessions: int | None = None,
                     ping: dict | None = None, ping_every_s: float = 20.0,
                     sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> int:
    """Consume a websocket forever (or `max_sessions` connections), reconnecting with
    exponential backoff. Returns the number of sessions run (for tests)."""
    sessions, backoff = 0, 1.0
    while max_sessions is None or sessions < max_sessions:
        sessions += 1
        try:
            ws = await connect(url)
            async with ws:
                for sub in subscribe or []:
                    await ws.send(json.dumps(sub))
                last_ping = time.monotonic()
                async for raw in ws:
                    on_message(json.loads(raw), time.time_ns())
                    backoff = 1.0
                    if ping and time.monotonic() - last_ping > ping_every_s:
                        await ws.send(json.dumps(ping))
                        last_ping = time.monotonic()
        except (OSError, asyncio.TimeoutError, ValueError, RuntimeError) as exc:  # noqa: PERF203
            print(f"[collector] {url[:60]}… disconnected: {type(exc).__name__}; retry in {backoff:.0f}s")
        except Exception as exc:  # websockets.ConnectionClosed and friends
            print(f"[collector] {url[:60]}… closed: {type(exc).__name__}; retry in {backoff:.0f}s")
        await sleep(backoff)
        backoff = min(backoff * 2, 60.0)
    return sessions


async def run_collector(cfg: CollectorConfig, connect: Connect | None = None,
                        max_sessions: int | None = None) -> None:  # pragma: no cover - network
    if connect is None:
        import websockets
        connect = lambda u: websockets.connect(u, max_size=2**22, ping_interval=20)  # noqa: E731
    tasks, writers = [], []
    if "binance_um" in cfg.venues:
        w = HourlyWriter(cfg.out_dir, "binance_um", cfg.flush_every)
        writers.append(w)
        tasks.append(run_stream(binance_url(cfg.symbols), lambda m, rx: w.write(normalize_binance(m, rx)),
                                connect, max_sessions=max_sessions))
    if "bybit" in cfg.venues:
        wb, st = HourlyWriter(cfg.out_dir, "bybit", cfg.flush_every), BybitState()
        writers.append(wb)
        tasks.append(run_stream(BYBIT_WS, lambda m, rx: wb.write(normalize_bybit(m, rx, st)), connect,
                                subscribe=bybit_subscriptions(cfg.symbols), ping={"op": "ping"},
                                max_sessions=max_sessions))
    try:
        await asyncio.gather(*tasks)
    finally:
        for w in writers:
            w.flush()


def latency_report(rec: pd.DataFrame) -> pd.DataFrame:
    """Receive-minus-exchange time per venue/type (ms): our real distance to each venue
    (includes clock offset; run chrony/NTP and compare medians, not absolutes)."""
    d = rec.assign(lat_ms=rec["rx_ns"] / 1e6 - rec["ts"].astype(float))
    return d.groupby(["venue", "type"])["lat_ms"].describe(percentiles=[0.5, 0.9, 0.99])[["count", "50%", "90%", "99%"]].replace(np.nan, 0)

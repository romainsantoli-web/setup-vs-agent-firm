import asyncio
import json

import pytest
from pydantic import ValidationError

from mft import collector as c

RX = 1_735_689_600_123_000_000  # 2025-01-01T00:00:00.123Z


def test_config_validation():
    assert c.CollectorConfig(symbols=("BTCUSDT",)).venues == ("binance_um", "bybit")
    for bad in (dict(symbols=("btc-usdt",)), dict(symbols=("BTCUSDT",), venues=("ftx",)),
                dict(symbols=("BTCUSDT",), out_dir="../x"), dict(symbols=())):
        with pytest.raises(ValidationError):
            c.CollectorConfig(**bad)


def test_binance_normalizer():
    agg = {"stream": "btcusdt@aggTrade", "data": {"e": "aggTrade", "s": "BTCUSDT", "p": "100.5", "q": "2", "T": 1, "m": True}}
    assert c.normalize_binance(agg, RX)[0]["side"] == "sell"
    bbo = {"e": "bookTicker", "s": "BTCUSDT", "b": "100", "B": "1", "a": "100.1", "A": "2", "T": 5}
    assert c.normalize_binance(bbo, RX)[0]["ask"] == 100.1
    mk = {"e": "markPriceUpdate", "E": 7, "s": "BTCUSDT", "p": "100", "i": "99.9", "r": "0.0001", "T": 9}
    assert c.normalize_binance(mk, RX)[0]["funding_rate"] == 0.0001
    liq = {"e": "forceOrder", "o": {"s": "ETHUSDT", "S": "SELL", "p": "10", "ap": "9.9", "q": "3", "z": "2", "T": 3}}
    r = c.normalize_binance(liq, RX)[0]
    assert r["liq_side"] == "long" and r["usd"] == pytest.approx(19.8)
    liq0 = {"e": "forceOrder", "o": {"s": "ETHUSDT", "S": "BUY", "p": "10", "ap": "0", "q": "3", "z": "0", "T": 3}}
    r0 = c.normalize_binance(liq0, RX)[0]
    assert r0["liq_side"] == "short" and r0["usd"] == 30
    assert c.normalize_binance({"e": "other"}, RX) == []


def test_bybit_normalizer_with_deltas():
    st = c.BybitState()
    assert c.normalize_bybit({"op": "pong"}, RX, st) == []
    tr = {"topic": "publicTrade.BTCUSDT", "data": [{"T": 1, "s": "BTCUSDT", "S": "Buy", "v": "0.1", "p": "100"}]}
    assert c.normalize_bybit(tr, RX, st)[0]["side"] == "buy"
    lq = {"topic": "allLiquidation.BTCUSDT", "data": [{"T": 1, "s": "BTCUSDT", "S": "Buy", "v": "2", "p": "50"}]}
    assert c.normalize_bybit(lq, RX, st)[0]["liq_side"] == "long"
    snap = {"topic": "orderbook.1.BTCUSDT", "type": "snapshot", "ts": 2, "cts": 1,
            "data": {"s": "BTCUSDT", "b": [["100", "1"]], "a": [["100.2", "3"]]}}
    assert c.normalize_bybit(snap, RX, st)[0]["bid"] == 100
    delta = {"topic": "orderbook.1.BTCUSDT", "type": "delta", "ts": 3,
             "data": {"s": "BTCUSDT", "b": [], "a": [["100.1", "1"]]}}
    r = c.normalize_bybit(delta, RX, st)[0]
    assert (r["bid"], r["ask"]) == (100.0, 100.1)
    half = {"topic": "orderbook.1.ETHUSDT", "type": "snapshot", "data": {"s": "ETHUSDT", "b": [["1", "1"]], "a": []}}
    assert c.normalize_bybit(half, RX, st) == []
    t1 = {"topic": "tickers.BTCUSDT", "type": "snapshot", "ts": 4,
          "data": {"symbol": "BTCUSDT", "markPrice": "100", "indexPrice": "99", "fundingRate": "0.0002",
                   "nextFundingTime": "123", "openInterestValue": "5e8"}}
    assert c.normalize_bybit(t1, RX, st)[0]["oi_usd"] == 5e8
    t2 = {"topic": "tickers.BTCUSDT", "type": "delta", "ts": 5, "data": {"symbol": "BTCUSDT", "markPrice": "101"}}
    r2 = c.normalize_bybit(t2, RX, st)[0]
    assert r2["mark"] == 101 and r2["index"] == 99
    t3 = {"topic": "tickers.XRPUSDT", "type": "snapshot", "ts": 4, "data": {"symbol": "XRPUSDT", "markPrice": "1"}}
    assert c.normalize_bybit(t3, RX, st) == []


def test_bybit_liq_side_flag(monkeypatch):
    monkeypatch.setattr(c, "BYBIT_LIQ_BUY_IS_LONG", False)
    lq = {"topic": "allLiquidation.BTCUSDT", "data": [{"T": 1, "s": "BTCUSDT", "S": "Buy", "v": "2", "p": "50"}]}
    assert c.normalize_bybit(lq, RX, c.BybitState())[0]["liq_side"] == "short"


def test_urls_and_subscriptions():
    u = c.binance_url(["BTCUSDT", "ETHUSDT"])
    assert u.startswith(c.BINANCE_WS) and "ethusdt@markPrice@1s" in u and u.endswith("!forceOrder@arr")
    subs = c.bybit_subscriptions(["A1", "B2", "C3"])
    assert [len(s["args"]) for s in subs] == [10, 2]


def test_writer_rotation_read_and_bars(tmp_path):
    w = c.HourlyWriter(str(tmp_path), "bybit", flush_every=2)
    h = 3_600_000_000_000
    m = 60_000_000_000
    recs = [
        {"venue": "bybit", "type": "bbo", "symbol": "BTCUSDT", "ts": 1_735_689_630_000, "rx_ns": RX, "bid": 100.0, "ask": 100.02},
        {"venue": "bybit", "type": "liquidation", "symbol": "BTCUSDT", "ts": 1_735_689_640_000, "rx_ns": RX + 1, "liq_side": "long", "usd": 5e4},
        {"venue": "bybit", "type": "mark", "symbol": "BTCUSDT", "ts": 1_735_689_650_000, "rx_ns": RX + 2, "mark": 100.1, "index": 100.0, "funding_rate": 0.0001, "oi_usd": 1e9},
        {"venue": "binance_um", "type": "bbo", "symbol": "BTCUSDT", "ts": 1_735_689_655_000, "rx_ns": RX + 3, "bid": 100.1, "ask": 100.12},
        {"venue": "bybit", "type": "liquidation", "symbol": "BTCUSDT", "ts": 1_735_689_600_000 + 61_000, "rx_ns": RX + m, "liq_side": "short", "usd": 2e4},
        {"venue": "bybit", "type": "bbo", "symbol": "BTCUSDT", "ts": 1_735_689_600_000 + 3_601_000, "rx_ns": RX + h, "bid": 101.0, "ask": 101.02},
    ]
    w.write(recs)
    w.flush()
    w.flush()  # no-op when empty
    files = sorted(tmp_path.rglob("*.jsonl.gz"))
    assert [f.name for f in files] == ["00.jsonl.gz", "01.jsonl.gz"]
    df = c.read_records(files)
    assert len(df) == 6
    bars = c.records_to_bar_columns(df, "BTCUSDT", "bybit", "1min", ref_venue="binance_um")
    first = bars.iloc[0]
    assert first["liq_long_usd"] == 5e4 and first["spread_bps"] == pytest.approx(2.0, rel=1e-3)
    assert first["funding_rate_bps"] == pytest.approx(1.0) and first["premium_bps"] == pytest.approx(10.0)
    assert first["close_ref"] == pytest.approx(100.11)
    assert bars["liq_short_usd"].sum() == 2e4
    lat = c.latency_report(df)
    assert set(lat.index.get_level_values(0)) == {"bybit", "binance_um"}
    assert c.read_records([]).empty


class FakeWS:
    def __init__(self, msgs, fail_after=False):
        self.msgs, self.sent, self.fail_after = msgs, [], fail_after

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def send(self, m):
        self.sent.append(json.loads(m))

    def __aiter__(self):
        self._it = iter(self.msgs)
        return self

    async def __anext__(self):
        try:
            return next(self._it)
        except StopIteration:
            if self.fail_after:
                raise RuntimeError("closed")
            raise StopAsyncIteration


def test_run_stream_reconnects_and_subscribes():
    got, sleeps, conns = [], [], []

    async def connect(url):
        if not conns:
            conns.append("fail")
            raise OSError("refused")
        ws = FakeWS([json.dumps({"a": 1}), json.dumps({"a": 2})], fail_after=len(conns) == 1)
        conns.append(ws)
        return ws

    async def fake_sleep(s):
        sleeps.append(s)

    n = asyncio.run(c.run_stream("wss://x", lambda m, rx: got.append(m["a"]), connect,
                                 subscribe=[{"op": "subscribe"}], max_sessions=3, ping={"op": "ping"},
                                 ping_every_s=0.0, sleep=fake_sleep))
    assert n == 3 and got == [1, 2, 1, 2]
    assert sleeps == [1.0, 1.0, 1.0]  # backoff resets after successful messages
    assert conns[1].sent[0] == {"op": "subscribe"} and {"op": "ping"} in conns[1].sent

    class Boom(Exception):
        pass

    async def connect_boom(url):
        raise Boom()
    assert asyncio.run(c.run_stream("wss://y", lambda m, rx: None, connect_boom, max_sessions=2,
                                    sleep=fake_sleep)) == 2
    assert sleeps[-1] == 2.0

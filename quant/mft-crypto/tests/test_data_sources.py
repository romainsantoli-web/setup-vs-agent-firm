import datetime as dt
import io
import json
import urllib.error
import zipfile

import pandas as pd
import pytest

from mft import data_sources as ds
from mft.models import DownloadRequest


def _req(**kw):
    base = dict(venue="binance_um", dataset="aggTrades", symbol="BTCUSDT",
                start=dt.date(2025, 1, 30), end=dt.date(2025, 2, 1), out_dir="data")
    return DownloadRequest(**{**base, **kw})


def test_build_urls():
    u = ds.build_urls(_req())
    assert len(u) == 3 and u[0].endswith("/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2025-01-30.zip")
    m = ds.build_urls(_req(dataset="fundingRate"))
    assert [x.rsplit("-", 2)[-2:] for x in m] == [["2025", "01.zip"], ["2025", "02.zip"]]
    k = ds.build_urls(_req(dataset="klines", interval="1m"))
    assert "/daily/klines/BTCUSDT/1m/BTCUSDT-1m-2025-01-30.zip" in k[0]
    b = ds.build_urls(_req(venue="bybit", dataset="trades"))
    assert b[0] == "https://public.bybit.com/trading/BTCUSDT/BTCUSDT2025-01-30.csv.gz"
    with pytest.raises(ValueError):
        ds.build_urls(_req(venue="bybit", dataset="aggTrades"))


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_download_with_retry_404_and_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(ds.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def opener(url, timeout):
        calls["n"] += 1
        if url.endswith("2025-01-31.zip"):
            raise urllib.error.HTTPError(url, 404, "nf", None, None)
        if url.endswith("2025-02-01.zip") and calls["n"] < 4:
            raise OSError("reset")
        return _Resp(b"payload")

    req = _req(out_dir=str(tmp_path))
    saved = ds.download(req, opener=opener)
    assert [p.name[-14:] for p in saved] == ["2025-01-30.zip", "2025-02-01.zip"]
    n_before = calls["n"]
    ds.download(req, opener=opener)  # cached files are not refetched
    assert calls["n"] == n_before + 1  # only the 404 day is retried

    def always_fail(url, timeout):
        raise OSError("down")
    with pytest.raises(OSError):
        ds.download(_req(out_dir=str(tmp_path / "x")), retries=2, opener=always_fail)


def _zip(tmp_path, text, name="a.zip"):
    p = tmp_path / name
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("a.csv", text)
    return p


def test_read_agg_trades_with_and_without_header(tmp_path):
    rows = "1,100.0,2.0,1,1,1735689600000,false\n2,101.0,1.0,2,2,1735689630000,true\n"
    hdr = "agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n"
    for name, text in (("h.zip", hdr + rows), ("n.zip", rows)):
        df = ds.read_binance_agg_trades(_zip(tmp_path, text, name))
        assert list(df["buyer_is_maker"]) == [False, True]
        assert df["ts"].iloc[0] == pd.Timestamp("2025-01-01", tz="UTC")


def test_trades_to_bars():
    t = pd.DataFrame({
        "ts": pd.to_datetime(["2025-01-01 00:00:10", "2025-01-01 00:00:50", "2025-01-01 00:02:30"], utc=True),
        "price": [100.0, 102.0, 101.0], "qty": [2000.0, 1.0, 1.0],
        "buyer_is_maker": [False, True, False],
    })
    b = ds.trades_to_bars(t, "1min", large_usd=100_000)
    first = b.iloc[0]
    assert first["buy_volume"] == 200_000 and first["sell_volume"] == 102
    assert first["large_buy_volume"] == 200_000 and first["large_sell_volume"] == 0
    assert b["n_trades"].tolist() == [2, 0, 1]
    assert b.iloc[1]["close"] == 102.0 and b.iloc[1]["low"] == 102.0  # empty bar carried forward


def _kreq(**kw):
    base = dict(venue="kraken_futures", dataset="candles", symbol="PF_XBTUSD",
                start=dt.date(2025, 1, 1), end=dt.date(2025, 1, 2), out_dir="data")
    return DownloadRequest(**{**base, **kw})


def test_kraken_request_validation():
    with pytest.raises(Exception):
        _kreq(symbol="BTCUSDT")  # kraken needs PF_ symbols
    with pytest.raises(Exception):
        _req(symbol="PF_XBTUSD")  # binance needs BTCUSDT-style
    with pytest.raises(Exception):
        _kreq(symbol="pf_xbt/usd")


def test_kraken_urls():
    u = ds.build_urls(_kreq())
    assert len(u) == 6 and u[0] == "https://futures.kraken.com/api/charts/v1/trade/PF_XBTUSD/1m?from=1735689600&to=1735776000"
    assert "/mark/" in u[1] and "/spot/" in u[2]
    e = ds.build_urls(_kreq(dataset="executions"))
    assert e[0].endswith("executions?since=1735689600000&before=1735776000000&sort=asc")
    f = ds.build_urls(_kreq(dataset="funding"))
    assert f == ["https://futures.kraken.com/derivatives/api/v4/historicalfundingrates?symbol=PF_XBTUSD"]
    with pytest.raises(ValueError):
        ds.build_urls(_kreq(dataset="aggTrades"))
    assert ds._filename(u[0]).endswith(".json") and "/" not in ds._filename(u[0])


def _exec(ts, px, qty, taker):
    return {"event": {"Execution": {"execution": {"timestamp": ts, "price": str(px), "quantity": str(qty),
                                                   "takerOrder": {"direction": taker}, "makerOrder": {}}}}}


def test_kraken_executions_pagination_parse_and_download(tmp_path):
    pages = {None: {"elements": [_exec(1735689600000, 100, 1, "Buy")], "continuationToken": "abc"},
             "abc": {"elements": [_exec(1735689601000, 101, 2, "Sell")]}}

    def opener(url, timeout):
        tok = url.split("continuationToken=")[1] if "continuationToken=" in url else None
        return _Resp(json.dumps(pages[tok]).encode())

    els = ds.fetch_kraken_executions("https://futures.kraken.com/x?since=1", opener)
    df = ds.read_kraken_executions(els)
    assert df["buyer_is_maker"].tolist() == [False, True] and df["qty"].sum() == 3
    assert ds.read_kraken_executions([]).empty
    saved = ds.download(_kreq(dataset="executions", end=dt.date(2025, 1, 1), out_dir=str(tmp_path)), opener=opener)
    assert len(json.loads(saved[0].read_text())) == 2


def test_kraken_candles():
    df = ds.read_kraken_candles({"candles": [{"time": 1735689600000, "open": "1", "high": "2", "low": "0.5",
                                              "close": "1.5", "volume": "10"}]})
    assert df["close"].iloc[0] == 1.5 and str(df.index.tz) == "UTC"
    assert ds.read_kraken_candles({}).empty

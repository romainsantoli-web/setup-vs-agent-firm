import datetime as dt
import io
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

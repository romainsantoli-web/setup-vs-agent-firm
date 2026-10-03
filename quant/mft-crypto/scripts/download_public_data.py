"""Download public archives (Binance UM / Bybit) for the research backfill.

    python scripts/download_public_data.py --venue binance_um --dataset aggTrades \
        --symbol BTCUSDT --start 2025-01-01 --end 2025-03-31 --out-dir data/raw
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mft.data_sources import download  # noqa: E402
from mft.models import DownloadRequest  # noqa: E402


def main(argv: list[str] | None = None) -> list[Path]:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--venue", required=True)
    p.add_argument("--dataset", required=True)
    p.add_argument("--symbol", required=True)
    p.add_argument("--start", required=True, type=dt.date.fromisoformat)
    p.add_argument("--end", required=True, type=dt.date.fromisoformat)
    p.add_argument("--out-dir", default="data/raw")
    p.add_argument("--interval", default="1m")
    a = p.parse_args(argv)
    req = DownloadRequest(venue=a.venue, dataset=a.dataset, symbol=a.symbol, start=a.start, end=a.end,
                          out_dir=a.out_dir, interval=a.interval)
    files = download(req)
    print(f"{len(files)} files in {req.out_dir}")
    return files


if __name__ == "__main__":
    main()

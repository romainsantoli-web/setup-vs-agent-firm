"""Run the live collector (deploy on the London VPS under systemd; see RESEARCH.md §7).

    python scripts/collect.py --symbols BTCUSDT ETHUSDT SOLUSDT --out-dir /data/live

Symbols are canonical (BTCUSDT); Kraken Futures subscribes to the matching PF_ perps
(BTCUSDT -> PF_XBTUSD). Kraken = execution venue; Binance/Bybit = information only.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mft.collector import CollectorConfig, run_collector  # noqa: E402


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--symbols", nargs="+", required=True)
    p.add_argument("--venues", nargs="+", default=["kraken_futures", "binance_um", "bybit"])
    p.add_argument("--out-dir", default="data/live")
    p.add_argument("--flush-every", type=int, default=500)
    a = p.parse_args(argv)
    cfg = CollectorConfig(symbols=tuple(a.symbols), venues=tuple(a.venues), out_dir=a.out_dir,
                          flush_every=a.flush_every)
    asyncio.run(run_collector(cfg))


if __name__ == "__main__":
    main()

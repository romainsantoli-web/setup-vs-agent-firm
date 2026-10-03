"""Pydantic models validating every external input of the research pipeline.

Rule (CLAUDE.md §2): every CLI argument / config entering the pipeline is validated here,
with length limits, slug regexes and path-traversal blocking.
"""

from __future__ import annotations

import datetime as dt
from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SYMBOL_RE = r"^[A-Z0-9]{2,20}$"
SLUG_RE = r"^[a-z0-9][a-z0-9_-]{0,39}$"


def _no_traversal(path: str) -> str:
    parts = PurePosixPath(path.replace("\\", "/")).parts
    if ".." in parts:
        raise ValueError("path traversal ('..') is not allowed")
    if "\x00" in path:
        raise ValueError("null byte in path")
    return path


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FeeTier(_Strict):
    name: str = Field(min_length=1, max_length=32)
    min_volume_usd: float = Field(ge=0)
    maker_bps: float = Field(ge=-5, le=10)  # negative = rebate
    taker_bps: float = Field(ge=0, le=20)


class FeeSchedule(_Strict):
    venue: str = Field(pattern=SLUG_RE)
    window_days: int = Field(ge=1, le=90)
    as_of: str = Field(min_length=4, max_length=32)
    verified: bool = False
    tiers: tuple[FeeTier, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def _monotone(self) -> "FeeSchedule":
        if self.tiers[0].min_volume_usd != 0:
            raise ValueError("first tier must start at 0 volume")
        for a, b in zip(self.tiers, self.tiers[1:]):
            if b.min_volume_usd <= a.min_volume_usd:
                raise ValueError("tier volume thresholds must be strictly increasing")
            if b.taker_bps > a.taker_bps or b.maker_bps > a.maker_bps:
                raise ValueError("fees must be non-increasing with tier")
        return self

    def tier_for_volume(self, volume_usd: float) -> FeeTier:
        """Highest tier whose threshold is met by the rolling-window volume."""
        best = self.tiers[0]
        for t in self.tiers:
            if volume_usd >= t.min_volume_usd:
                best = t
        return best


class CostParams(_Strict):
    """Market-microstructure cost parameters for one instrument."""

    half_spread_bps: float = Field(ge=0, le=100)
    impact_coef: float = Field(default=0.1, ge=0, le=10)  # square-root law coefficient
    daily_vol_bps: float = Field(default=300.0, gt=0, le=5000)
    adv_usd: float = Field(default=1e9, gt=0)
    # Expected adverse markout of one passive fill (bps). None -> equal to the half-spread:
    # a non-colocated order sits at the back of the queue and is filled mostly when the level
    # breaks, so on average it does NOT earn the spread. Calibrate from our own fills' markouts.
    adverse_bps: float | None = Field(default=None, ge=0, le=100)


class BacktestConfig(_Strict):
    k_in: float = Field(default=1.5, gt=0, le=10)
    k_out: float = Field(default=0.0, ge=0, le=10)
    max_hold_bars: int = Field(default=60, ge=1, le=100_000)
    min_hold_bars: int = Field(default=1, ge=0, le=100_000)
    execution: Literal["taker", "maker_entry", "maker_both"] = "taker"
    maker_offset_bps: float = Field(default=0.0, ge=0, le=50)
    fill_window_bars: int = Field(default=1, ge=1, le=1000)
    chase_unfilled: bool = False
    notional_usd: float = Field(default=10_000.0, gt=0, le=1e9)
    bars_per_day: float = Field(default=1440.0, gt=0)

    @model_validator(mode="after")
    def _bands(self) -> "BacktestConfig":
        if self.k_out >= self.k_in:
            raise ValueError("k_out must be < k_in (hysteresis band)")
        if self.min_hold_bars > self.max_hold_bars:
            raise ValueError("min_hold_bars must be <= max_hold_bars")
        return self


class DownloadRequest(_Strict):
    venue: Literal["binance_um", "bybit"]
    dataset: Literal["aggTrades", "trades", "bookTicker", "fundingRate", "metrics", "premiumIndexKlines", "klines"]
    symbol: str = Field(pattern=SYMBOL_RE)
    start: dt.date
    end: dt.date
    out_dir: str = Field(min_length=1, max_length=512)
    interval: str = Field(default="1m", pattern=r"^(1s|1m|5m|15m|1h)$")

    @field_validator("out_dir")
    @classmethod
    def _path(cls, v: str) -> str:
        return _no_traversal(v)

    @model_validator(mode="after")
    def _dates(self) -> "DownloadRequest":
        if self.end < self.start:
            raise ValueError("end must be >= start")
        if (self.end - self.start).days > 3 * 366:
            raise ValueError("range limited to 3 years per request")
        return self


class StudyConfig(_Strict):
    n_symbols: int = Field(default=6, ge=1, le=200)
    n_days: int = Field(default=30, ge=2, le=3650)
    bars_per_day: int = Field(default=1440, ge=24, le=86_400)
    seed: int = Field(default=7, ge=0, le=2**31 - 1)
    planted: bool = True
    horizons: tuple[int, ...] = Field(default=(1, 5, 15, 30, 60), min_length=1, max_length=16)
    out_path: str = Field(default="reports/synthetic_study.md", min_length=1, max_length=512)

    @field_validator("out_path")
    @classmethod
    def _path(cls, v: str) -> str:
        return _no_traversal(v)

    @field_validator("horizons")
    @classmethod
    def _h(cls, v: tuple[int, ...]) -> tuple[int, ...]:
        if any(h < 1 or h > 10_000 for h in v):
            raise ValueError("horizons must be in [1, 10000] bars")
        return tuple(sorted(set(v)))

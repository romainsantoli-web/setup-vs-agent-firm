"""Read-only verification of Kraken Futures PERP fees and max leverage — run FROM THE VPS.

Standard library only (no pip install into the shared venv). Only HTTP GET requests: it never
places orders and never changes leverage preferences. A handful of REST calls in total, so it
does not compete with the running websocket recorders.

    ~/venv/bin/python kraken_check.py --out ~/quant-desk/kraken_check/report.json
    # account-specific part (fee tier reached, max leverage allowed for THIS account / EU entity):
    KRAKEN_FUTURES_API_KEY=... KRAKEN_FUTURES_API_SECRET=... ~/venv/bin/python kraken_check.py --private
    # or: --env-file /path/to/.env   (keys are read, never printed: only the last 4 chars appear)

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
Response shapes follow Kraken's public docs as known to the author; unknown shapes are kept raw
in the report instead of crashing.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path, PurePosixPath

BASE = "https://futures.kraken.com"
PUBLIC = {"feeschedules": "/derivatives/api/v3/feeschedules",
          "instruments": "/derivatives/api/v3/instruments"}
PRIVATE = {"volumes": "/derivatives/api/v3/feeschedules/volumes",
           "leverage": "/derivatives/api/v3/leveragepreferences"}
PERP_RE = re.compile(r"^PF_[A-Z0-9]{2,15}USD$")
DISCLAIMER = "⚠️ Contenu généré par IA — validation humaine requise avant utilisation."


def mask(secret: str | None) -> str:
    if not secret:
        return "<absent>"
    return "****" + secret[-4:] if len(secret) > 4 else "****"


def safe_out(path: str) -> Path:
    if len(path) > 512 or ".." in PurePosixPath(path.replace("\\", "/")).parts or "\x00" in path:
        raise ValueError("invalid --out path (no '..', max 512 chars)")
    return Path(os.path.expanduser(path))


def sign(endpoint: str, nonce: str, secret_b64: str, post_data: str = "") -> str:
    """Kraken Futures v3 Authent: b64(HMAC-SHA512(b64dec(secret), SHA256(postData+nonce+path)))
    where path is the endpoint WITHOUT the '/derivatives' prefix."""
    path = endpoint[len("/derivatives"):] if endpoint.startswith("/derivatives") else endpoint
    digest = hashlib.sha256((post_data + nonce + path).encode()).digest()
    mac = hmac.new(base64.b64decode(secret_b64), digest, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()


def get(endpoint: str, opener=urllib.request.urlopen, key: str | None = None, secret: str | None = None) -> dict:
    req = urllib.request.Request(BASE + endpoint, method="GET")
    req.add_header("User-Agent", "mft-kraken-check/1.0")
    if key and secret:
        nonce = str(int(time.time() * 1000))
        req.add_header("APIKey", key)
        req.add_header("Nonce", nonce)
        req.add_header("Authent", sign(endpoint, nonce, secret))
    with opener(req, timeout=30) as resp:
        return json.loads(resp.read())


def parse_fee_schedules(payload: dict) -> list[dict]:
    """Fees come in PERCENT from the API -> converted to bps."""
    out = []
    for sch in payload.get("feeSchedules", []):
        tiers = [{"min_volume_usd": float(t.get("usdVolume", 0)),
                  "maker_bps": round(float(t["makerFee"]) * 100, 4),
                  "taker_bps": round(float(t["takerFee"]) * 100, 4)} for t in sch.get("tiers", [])]
        out.append({"uid": sch.get("uid"), "name": sch.get("name"),
                    "tiers": sorted(tiers, key=lambda x: x["min_volume_usd"])})
    return out


def _max_lev(levels: list[dict] | None) -> float | None:
    if not levels:
        return None
    im = float(levels[0].get("initialMargin", 0) or 0)
    return round(1.0 / im, 2) if im > 0 else None


def parse_perps(payload: dict) -> list[dict]:
    rows = []
    for ins in payload.get("instruments", []):
        sym = ins.get("symbol", "")
        if not PERP_RE.match(sym):
            continue
        rows.append({"symbol": sym, "tradeable": ins.get("tradeable"),
                     "max_leverage_standard": _max_lev(ins.get("marginLevels")),
                     "max_leverage_retail": _max_lev(ins.get("retailMarginLevels")),
                     "first_tier_max_units": (ins.get("marginLevels") or [{}])[0].get("numNonContractUnits"),
                     "tick_size": ins.get("tickSize"), "contract_size": ins.get("contractSize"),
                     "fee_schedule_uid": ins.get("feeScheduleUid"), "tags": ins.get("tags")})
    return rows


def load_env_file(path: str) -> dict[str, str]:
    env = {}
    for line in Path(os.path.expanduser(path)).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def run(argv: list[str] | None = None, opener=urllib.request.urlopen, environ: dict | None = None) -> dict:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="~/quant-desk/kraken_check/report.json")
    p.add_argument("--private", action="store_true", help="also query account fee volume + max leverage (GET only)")
    p.add_argument("--env-file", default=None)
    a = p.parse_args(argv)
    out = safe_out(a.out)
    env = dict(os.environ if environ is None else environ)
    if a.env_file:
        env.update(load_env_file(a.env_file))

    report: dict = {"disclaimer": DISCLAIMER, "queried_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "host": BASE, "scope": "Kraken Futures perpetuals (PF_*) only"}
    fees = get(PUBLIC["feeschedules"], opener)
    report["fee_schedules"] = parse_fee_schedules(fees)
    perps = parse_perps(get(PUBLIC["instruments"], opener))
    report["perps"] = perps
    used = {r["fee_schedule_uid"] for r in perps}
    report["perp_fee_schedules"] = [s for s in report["fee_schedules"] if s["uid"] in used]

    if a.private:
        key, secret = env.get("KRAKEN_FUTURES_API_KEY"), env.get("KRAKEN_FUTURES_API_SECRET")
        report["api_key"] = mask(key)
        if not (key and secret):
            report["private"] = "skipped: KRAKEN_FUTURES_API_KEY / KRAKEN_FUTURES_API_SECRET not set"
        else:
            priv = {}
            for name, ep in PRIVATE.items():
                try:
                    priv[name] = get(ep, opener, key, secret)
                except Exception as exc:  # noqa: BLE001 — report, never crash, never echo secrets
                    priv[name] = {"error": type(exc).__name__, "detail": str(exc)[:200].replace(secret, "****").replace(key, "****")}
            report["private"] = priv
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:  # pragma: no cover
    r = run()
    for s in r["perp_fee_schedules"]:
        print(f"[fees] {s['name']} ({s['uid']}):")
        for t in s["tiers"]:
            print(f"   >= {t['min_volume_usd']:>14,.0f} USD  maker {t['maker_bps']:>6} bps  taker {t['taker_bps']:>6} bps")
    for row in r["perps"]:
        print(f"[perp] {row['symbol']:<12} max lev standard={row['max_leverage_standard']} retail={row['max_leverage_retail']}")
    if "private" in r:
        print("[private]", json.dumps(r["private"], ensure_ascii=False)[:2000])
    print(DISCLAIMER)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

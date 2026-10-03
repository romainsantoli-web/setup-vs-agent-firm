import base64
import hashlib
import hmac
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import kraken_check as kc  # noqa: E402

FEES = {"result": "success", "feeSchedules": [
    {"uid": "u-perp", "name": "PerpFees", "tiers": [{"makerFee": 0.02, "takerFee": 0.05, "usdVolume": 0.0},
                                                   {"makerFee": 0.0, "takerFee": 0.01, "usdVolume": 100000000.0}]},
    {"uid": "u-other", "name": "Other", "tiers": [{"makerFee": 0.1, "takerFee": 0.2, "usdVolume": 0.0}]}]}
INSTR = {"result": "success", "instruments": [
    {"symbol": "PF_XBTUSD", "tradeable": True, "feeScheduleUid": "u-perp",
     "marginLevels": [{"numNonContractUnits": 0, "initialMargin": 0.02, "maintenanceMargin": 0.01}],
     "retailMarginLevels": [{"numNonContractUnits": 0, "initialMargin": 0.5, "maintenanceMargin": 0.25}]},
    {"symbol": "PF_ETHUSD", "tradeable": True, "feeScheduleUid": "u-perp", "marginLevels": []},
    {"symbol": "FI_XBTUSD_250926", "feeScheduleUid": "u-other"}]}


class R(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def make_opener(seen, fail_private=False):
    def opener(req, timeout):
        seen.append(req)
        assert req.get_method() == "GET"  # read-only, always
        url = req.full_url
        if url.endswith("/feeschedules"):
            return R(json.dumps(FEES).encode())
        if url.endswith("/instruments"):
            return R(json.dumps(INSTR).encode())
        if fail_private:
            raise OSError("denied for KEYabcd1234")
        return R(json.dumps({"result": "success", "x": url.rsplit("/", 1)[1]}).encode())
    return opener


def test_public_report(tmp_path):
    seen = []
    out = tmp_path / "r.json"
    r = kc.run(["--out", str(out)], opener=make_opener(seen), environ={})
    assert [p["symbol"] for p in r["perps"]] == ["PF_XBTUSD", "PF_ETHUSD"]  # dated futures excluded
    assert r["perps"][0]["max_leverage_standard"] == 50.0 and r["perps"][0]["max_leverage_retail"] == 2.0
    assert r["perps"][1]["max_leverage_standard"] is None
    sch = r["perp_fee_schedules"]
    assert len(sch) == 1 and sch[0]["tiers"][0] == {"min_volume_usd": 0.0, "maker_bps": 2.0, "taker_bps": 5.0}
    assert sch[0]["tiers"][1]["taker_bps"] == 1.0
    assert "private" not in r and json.loads(out.read_text())["disclaimer"].startswith("⚠️")
    assert len(seen) == 2


def test_private_signed_and_secrets_never_written(tmp_path):
    secret = base64.b64encode(b"s3cret-bytes-xyz").decode()
    env = {"KRAKEN_FUTURES_API_KEY": "KEYabcd1234", "KRAKEN_FUTURES_API_SECRET": secret}
    seen = []
    out = tmp_path / "r.json"
    r = kc.run(["--out", str(out), "--private"], opener=make_opener(seen), environ=env)
    assert r["api_key"] == "****1234" and set(r["private"]) == {"volumes", "leverage"}
    priv_req = seen[2]
    assert priv_req.get_header("Apikey") == "KEYabcd1234" and priv_req.get_header("Authent")
    text = out.read_text()
    assert "KEYabcd1234" not in text and secret not in text
    # error path redacts the key too
    r2 = kc.run(["--out", str(out), "--private"], opener=make_opener([], fail_private=True), environ=env)
    assert "KEYabcd1234" not in json.dumps(r2) and r2["private"]["volumes"]["error"] == "OSError"


def test_private_without_keys_is_skipped_and_env_file(tmp_path):
    r = kc.run(["--out", str(tmp_path / "a.json"), "--private"], opener=make_opener([]), environ={})
    assert r["private"].startswith("skipped") and r["api_key"] == "<absent>"
    envf = tmp_path / ".env"
    envf.write_text("# keys\nKRAKEN_FUTURES_API_KEY='k1234'\nKRAKEN_FUTURES_API_SECRET=\"" +
                    base64.b64encode(b"x").decode() + "\"\n\n")
    r2 = kc.run(["--out", str(tmp_path / "b.json"), "--private", "--env-file", str(envf)],
                opener=make_opener([]), environ={})
    assert r2["api_key"] == "****1234" and isinstance(r2["private"], dict)


def test_sign_matches_kraken_recipe():
    secret = base64.b64encode(b"key").decode()
    got = kc.sign("/derivatives/api/v3/feeschedules/volumes", "123", secret)
    digest = hashlib.sha256(b"123/api/v3/feeschedules/volumes").digest()
    want = base64.b64encode(hmac.new(b"key", digest, hashlib.sha512).digest()).decode()
    assert got == want
    assert kc.sign("/api/v3/x", "1", secret) == kc.sign("/derivatives/api/v3/x", "1", secret)


def test_bad_out_path_and_mask():
    with pytest.raises(ValueError):
        kc.safe_out("../../etc/x.json")
    with pytest.raises(ValueError):
        kc.run(["--out", "a/../b.json"], opener=make_opener([]), environ={})
    assert kc.mask("ab") == "****" and kc.mask(None) == "<absent>"

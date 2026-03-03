"""Tests for firm config models and French/multilingual model support.

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

from unittest.mock import patch


from firm_cli.config import (
    DEFAULTS,
    RECOMMENDED_MODELS,
    _config_models,
    _config_set,
    _load_config,
    _save_config,
    run_config,
)


# ── RECOMMENDED_MODELS ──────────────────────────────────────────────────────


def test_recommended_models_not_empty():
    assert len(RECOMMENDED_MODELS) >= 4


def test_recommended_models_have_required_fields():
    for name, info in RECOMMENDED_MODELS.items():
        assert "lang" in info, f"{name} missing lang"
        assert "dim" in info, f"{name} missing dim"
        assert "speed" in info, f"{name} missing speed"
        assert "note" in info, f"{name} missing note"
        assert info["dim"] > 0


def test_recommended_models_include_default():
    assert DEFAULTS["memory.model"] in RECOMMENDED_MODELS


def test_recommended_models_include_french():
    french_models = [
        name for name, info in RECOMMENDED_MODELS.items()
        if "french" in info["lang"].lower() or "50+" in info["lang"]
    ]
    assert len(french_models) >= 2, "Should have at least 2 French-capable models"


def test_recommended_models_include_multilingual():
    multilingual = [
        name for name, info in RECOMMENDED_MODELS.items()
        if "multilingual" in name.lower() or "100+" in info["lang"] or "50+" in info["lang"]
    ]
    assert len(multilingual) >= 2


# ── DEFAULTS ────────────────────────────────────────────────────────────────


def test_defaults_contain_model():
    assert "memory.model" in DEFAULTS
    assert DEFAULTS["memory.model"] == "all-MiniLM-L6-v2"


# ── _config_models ──────────────────────────────────────────────────────────


def test_config_models_returns_zero():
    ret = _config_models()
    assert ret == 0


# ── _config_set model hint ──────────────────────────────────────────────────


def test_config_set_model_known(tmp_path):
    with patch("firm_cli.config.CONFIG_FILE", tmp_path / "config.json"):
        ret = _config_set("memory.model", "paraphrase-multilingual-MiniLM-L12-v2")
        assert ret == 0


def test_config_set_model_unknown(tmp_path):
    with patch("firm_cli.config.CONFIG_FILE", tmp_path / "config.json"):
        ret = _config_set("memory.model", "custom-model-xyz")
        assert ret == 0


def test_config_set_non_model(tmp_path):
    with patch("firm_cli.config.CONFIG_FILE", tmp_path / "config.json"):
        ret = _config_set("server.host", "0.0.0.0")
        assert ret == 0


# ── run_config models subcommand ────────────────────────────────────────────


def test_run_config_models():
    import argparse
    args = argparse.Namespace(config_command="models")
    ret = run_config(args)
    assert ret == 0


# ── CLI integration ──────────────────────────────────────────────────────────


def test_cli_config_models_subcommand():
    from firm_cli.main import _build_parser
    parser = _build_parser()
    args = parser.parse_args(["config", "models"])
    assert args.config_command == "models"


# ── _load_config / _save_config roundtrip ────────────────────────────────────


def test_config_roundtrip(tmp_path):
    cfg_file = tmp_path / "config.json"
    with patch("firm_cli.config.CONFIG_FILE", cfg_file):
        _save_config({"memory.model": "paraphrase-multilingual-MiniLM-L12-v2", "custom": "val"})
        config = _load_config()
        assert config["memory.model"] == "paraphrase-multilingual-MiniLM-L12-v2"
        assert config["custom"] == "val"
        # Defaults still present
        assert config["server.host"] == "127.0.0.1"

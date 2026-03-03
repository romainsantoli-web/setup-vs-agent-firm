"""Tests for memory backend plugin system (SQLite only — no external deps).

Redis and PostgreSQL backends require running services and are tested
via integration tests when those services are available.

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import os

import pytest

from integrations.memory_backends import (
    MemoryBackend,
    MemoryRecord,
    SQLiteBackend,
    get_backend,
    list_backends,
)


# ── Factory ──────────────────────────────────────────────────────────────────


def test_list_backends():
    names = list_backends()
    assert "sqlite" in names
    assert "redis" in names
    assert "postgres" in names


def test_get_backend_sqlite(tmp_path):
    db = str(tmp_path / "test.db")
    backend = get_backend("sqlite", path=db)
    assert isinstance(backend, SQLiteBackend)


def test_get_backend_unknown():
    with pytest.raises(ValueError, match="Unknown backend"):
        get_backend("cassandra")


# ── SQLiteBackend full lifecycle ─────────────────────────────────────────────


@pytest.fixture
def backend(tmp_path):
    db = str(tmp_path / "test.db")
    return SQLiteBackend(path=db)


def test_store_and_get(backend):
    backend.store("key-1", {"text": "Hello", "weight": 0.9})
    record = backend.get("key-1")
    assert record is not None
    assert isinstance(record, MemoryRecord)
    assert record.key == "key-1"
    assert record.data["text"] == "Hello"
    assert record.data["weight"] == 0.9
    assert record.created_at > 0
    assert record.updated_at >= record.created_at


def test_get_nonexistent(backend):
    assert backend.get("no-such-key") is None


def test_store_upsert(backend):
    backend.store("k", {"v": 1})
    backend.store("k", {"v": 2})
    record = backend.get("k")
    assert record.data["v"] == 2


def test_store_with_metadata(backend):
    backend.store("k", {"text": "hi"}, metadata={"source": "test", "version": 3})
    record = backend.get("k")
    assert record.metadata["source"] == "test"
    assert record.metadata["version"] == 3


def test_search(backend):
    backend.store("rule-1", {"text": "Always run pytest before push"})
    backend.store("rule-2", {"text": "Use Pydantic for validation"})
    backend.store("rule-3", {"text": "Run linter on every commit"})

    results = backend.search("pytest")
    assert len(results) == 1
    assert results[0].key == "rule-1"


def test_search_no_match(backend):
    backend.store("rule-1", {"text": "Hello world"})
    results = backend.search("nonexistent-query-xyz")
    assert results == []


def test_search_limit(backend):
    for i in range(20):
        backend.store(f"k-{i:03d}", {"text": f"test pattern {i}"})
    results = backend.search("test pattern", limit=5)
    assert len(results) == 5


def test_delete(backend):
    backend.store("k", {"text": "temp"})
    assert backend.delete("k") is True
    assert backend.get("k") is None


def test_delete_nonexistent(backend):
    assert backend.delete("nope") is False


def test_list_keys(backend):
    backend.store("alpha-1", {"x": 1})
    backend.store("alpha-2", {"x": 2})
    backend.store("beta-1", {"x": 3})

    all_keys = backend.list_keys()
    assert sorted(all_keys) == ["alpha-1", "alpha-2", "beta-1"]

    alpha_keys = backend.list_keys(prefix="alpha")
    assert sorted(alpha_keys) == ["alpha-1", "alpha-2"]

    beta_keys = backend.list_keys(prefix="beta")
    assert beta_keys == ["beta-1"]


def test_count(backend):
    assert backend.count() == 0
    backend.store("a", {"x": 1})
    backend.store("b", {"x": 2})
    assert backend.count() == 2


def test_clear(backend):
    backend.store("a", {"x": 1})
    backend.store("b", {"x": 2})
    deleted = backend.clear()
    assert deleted == 2
    assert backend.count() == 0


def test_clear_empty(backend):
    assert backend.clear() == 0


def test_health(backend):
    backend.store("x", {"v": 1})
    h = backend.health()
    assert h["ok"] is True
    assert h["backend"] == "SQLiteBackend"
    assert h["count"] == 1
    assert "path" in h


# ── MemoryRecord dataclass ──────────────────────────────────────────────────


def test_memory_record_defaults():
    rec = MemoryRecord(key="k", data={"text": "test"})
    assert rec.key == "k"
    assert rec.data == {"text": "test"}
    assert rec.created_at > 0
    assert rec.updated_at >= rec.created_at
    assert rec.metadata == {}


def test_memory_record_custom():
    rec = MemoryRecord(
        key="k", data={"text": "test"},
        created_at=100.0, updated_at=200.0,
        metadata={"source": "import"},
    )
    assert rec.created_at == 100.0
    assert rec.updated_at == 200.0
    assert rec.metadata["source"] == "import"


# ── Edge cases ──────────────────────────────────────────────────────────────


def test_unicode_data(backend):
    backend.store("unicode", {"text": "日本語テスト 🧠 mémoire"})
    record = backend.get("unicode")
    assert "日本語" in record.data["text"]
    assert "🧠" in record.data["text"]


def test_large_data(backend):
    big = {"text": "x" * 100_000, "items": list(range(1000))}
    backend.store("big", big)
    record = backend.get("big")
    assert len(record.data["text"]) == 100_000
    assert len(record.data["items"]) == 1000


def test_empty_search_query(backend):
    backend.store("k", {"text": "anything"})
    results = backend.search("")
    assert len(results) >= 1


def test_special_chars_in_key(backend):
    backend.store("key/with/slashes", {"x": 1})
    backend.store("key with spaces", {"x": 2})
    assert backend.get("key/with/slashes").data["x"] == 1
    assert backend.get("key with spaces").data["x"] == 2

"""Memory backend plugin system — abstract interface for pluggable storage.

Supports:
  - SQLite (default, zero-dependency)
  - Redis (optional, for distributed setups)
  - PostgreSQL + pgvector (optional, for production)

Usage:
    from integrations.memory_backends import get_backend
    backend = get_backend("sqlite", path="./memory.db")
    backend.store("rule-1", {"weight": 0.85, "text": "Always run tests"})
    results = backend.search("tests", limit=5)

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MemoryRecord:
    """A single memory record stored in the backend."""
    key: str
    data: dict[str, Any]
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryBackend(ABC):
    """Abstract interface for memory storage backends."""

    @abstractmethod
    def store(self, key: str, data: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        """Store or update a memory record."""

    @abstractmethod
    def get(self, key: str) -> MemoryRecord | None:
        """Retrieve a single record by key."""

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[MemoryRecord]:
        """Search records by text query."""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a record. Returns True if found and deleted."""

    @abstractmethod
    def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys, optionally filtered by prefix."""

    @abstractmethod
    def count(self) -> int:
        """Return total number of records."""

    @abstractmethod
    def clear(self) -> int:
        """Delete all records. Returns count of deleted records."""

    def health(self) -> dict[str, Any]:
        """Health check for the backend."""
        return {"backend": self.__class__.__name__, "ok": True, "count": self.count()}


# ── SQLite Backend (default) ─────────────────────────────────────────────────

class SQLiteBackend(MemoryBackend):
    """SQLite-based memory backend. Zero external dependencies."""

    def __init__(self, path: str = "./firm-memory.db"):
        import sqlite3
        self._path = path
        self._conn = sqlite3.connect(path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_updated ON memory(updated_at)
        """)
        self._conn.commit()

    def store(self, key: str, data: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        now = time.time()
        self._conn.execute(
            """INSERT INTO memory (key, data, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET data=?, metadata=?, updated_at=?""",
            (key, json.dumps(data), json.dumps(metadata or {}), now, now,
             json.dumps(data), json.dumps(metadata or {}), now),
        )
        self._conn.commit()

    def get(self, key: str) -> MemoryRecord | None:
        row = self._conn.execute(
            "SELECT key, data, metadata, created_at, updated_at FROM memory WHERE key = ?",
            (key,),
        ).fetchone()
        if not row:
            return None
        return MemoryRecord(
            key=row[0], data=json.loads(row[1]), metadata=json.loads(row[2]),
            created_at=row[3], updated_at=row[4],
        )

    def search(self, query: str, limit: int = 10) -> list[MemoryRecord]:
        rows = self._conn.execute(
            "SELECT key, data, metadata, created_at, updated_at FROM memory WHERE data LIKE ? ORDER BY updated_at DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [
            MemoryRecord(key=r[0], data=json.loads(r[1]), metadata=json.loads(r[2]),
                         created_at=r[3], updated_at=r[4])
            for r in rows
        ]

    def delete(self, key: str) -> bool:
        cur = self._conn.execute("DELETE FROM memory WHERE key = ?", (key,))
        self._conn.commit()
        return cur.rowcount > 0

    def list_keys(self, prefix: str = "") -> list[str]:
        rows = self._conn.execute(
            "SELECT key FROM memory WHERE key LIKE ? ORDER BY key",
            (f"{prefix}%",),
        ).fetchall()
        return [r[0] for r in rows]

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]

    def clear(self) -> int:
        count = self.count()
        self._conn.execute("DELETE FROM memory")
        self._conn.commit()
        return count

    def health(self) -> dict[str, Any]:
        base = super().health()
        base["path"] = self._path
        return base


# ── Redis Backend ─────────────────────────────────────────────────────────────

class RedisBackend(MemoryBackend):
    """Redis-based memory backend for distributed setups.

    Requires: pip install redis
    """

    def __init__(self, url: str = "redis://localhost:6379/0", prefix: str = "firm:memory:"):
        try:
            import redis
        except ImportError:
            raise ImportError("Redis backend requires: pip install redis")
        self._prefix = prefix
        self._redis = redis.Redis.from_url(url, decode_responses=True)

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def store(self, key: str, data: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        now = time.time()
        record = {
            "data": json.dumps(data),
            "metadata": json.dumps(metadata or {}),
            "created_at": str(now),
            "updated_at": str(now),
        }
        rk = self._key(key)
        existing = self._redis.hget(rk, "created_at")
        if existing:
            record["created_at"] = existing
        self._redis.hset(rk, mapping=record)

    def get(self, key: str) -> MemoryRecord | None:
        data = self._redis.hgetall(self._key(key))
        if not data:
            return None
        return MemoryRecord(
            key=key, data=json.loads(data["data"]),
            metadata=json.loads(data.get("metadata", "{}")),
            created_at=float(data.get("created_at", 0)),
            updated_at=float(data.get("updated_at", 0)),
        )

    def search(self, query: str, limit: int = 10) -> list[MemoryRecord]:
        results = []
        for rk in self._redis.scan_iter(match=f"{self._prefix}*", count=100):
            if len(results) >= limit:
                break
            data = self._redis.hgetall(rk)
            if query.lower() in data.get("data", "").lower():
                key = rk[len(self._prefix):] if rk.startswith(self._prefix) else rk
                results.append(MemoryRecord(
                    key=key, data=json.loads(data["data"]),
                    metadata=json.loads(data.get("metadata", "{}")),
                    created_at=float(data.get("created_at", 0)),
                    updated_at=float(data.get("updated_at", 0)),
                ))
        return results

    def delete(self, key: str) -> bool:
        return self._redis.delete(self._key(key)) > 0

    def list_keys(self, prefix: str = "") -> list[str]:
        pattern = f"{self._prefix}{prefix}*"
        keys = []
        for rk in self._redis.scan_iter(match=pattern, count=100):
            k = rk[len(self._prefix):] if rk.startswith(self._prefix) else rk
            keys.append(k)
        return sorted(keys)

    def count(self) -> int:
        return sum(1 for _ in self._redis.scan_iter(match=f"{self._prefix}*", count=100))

    def clear(self) -> int:
        keys = list(self._redis.scan_iter(match=f"{self._prefix}*", count=100))
        if keys:
            return self._redis.delete(*keys)
        return 0

    def health(self) -> dict[str, Any]:
        base = super().health()
        try:
            self._redis.ping()
            base["connected"] = True
        except Exception as e:
            base["connected"] = False
            base["error"] = str(e)
        return base


# ── PostgreSQL + pgvector Backend ─────────────────────────────────────────────

class PostgresBackend(MemoryBackend):
    """PostgreSQL backend with optional pgvector support.

    Requires: pip install psycopg2-binary
    Optional: CREATE EXTENSION vector;  (for similarity search)
    """

    def __init__(self, dsn: str = "postgresql://localhost:5432/firm", table: str = "firm_memory"):
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            raise ImportError("PostgreSQL backend requires: pip install psycopg2-binary")
        import psycopg2
        self._table = table
        self._conn = psycopg2.connect(dsn)
        self._conn.autocommit = True
        with self._conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    key TEXT PRIMARY KEY,
                    data JSONB NOT NULL,
                    metadata JSONB DEFAULT '{{}}',
                    created_at DOUBLE PRECISION NOT NULL,
                    updated_at DOUBLE PRECISION NOT NULL
                )
            """)
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_updated ON {table}(updated_at)")

    def store(self, key: str, data: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        now = time.time()
        with self._conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self._table} (key, data, metadata, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET data = %s, metadata = %s, updated_at = %s
            """, (key, json.dumps(data), json.dumps(metadata or {}), now, now,
                  json.dumps(data), json.dumps(metadata or {}), now))

    def get(self, key: str) -> MemoryRecord | None:
        with self._conn.cursor() as cur:
            cur.execute(
                f"SELECT key, data, metadata, created_at, updated_at FROM {self._table} WHERE key = %s",
                (key,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return MemoryRecord(
                key=row[0], data=row[1] if isinstance(row[1], dict) else json.loads(row[1]),
                metadata=row[2] if isinstance(row[2], dict) else json.loads(row[2]),
                created_at=row[3], updated_at=row[4],
            )

    def search(self, query: str, limit: int = 10) -> list[MemoryRecord]:
        with self._conn.cursor() as cur:
            cur.execute(
                f"SELECT key, data, metadata, created_at, updated_at FROM {self._table} "
                f"WHERE data::text ILIKE %s ORDER BY updated_at DESC LIMIT %s",
                (f"%{query}%", limit),
            )
            return [
                MemoryRecord(
                    key=r[0], data=r[1] if isinstance(r[1], dict) else json.loads(r[1]),
                    metadata=r[2] if isinstance(r[2], dict) else json.loads(r[2]),
                    created_at=r[3], updated_at=r[4],
                )
                for r in cur.fetchall()
            ]

    def delete(self, key: str) -> bool:
        with self._conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self._table} WHERE key = %s", (key,))
            return cur.rowcount > 0

    def list_keys(self, prefix: str = "") -> list[str]:
        with self._conn.cursor() as cur:
            cur.execute(
                f"SELECT key FROM {self._table} WHERE key LIKE %s ORDER BY key",
                (f"{prefix}%",),
            )
            return [r[0] for r in cur.fetchall()]

    def count(self) -> int:
        with self._conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self._table}")
            return cur.fetchone()[0]

    def clear(self) -> int:
        with self._conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self._table}")
            count = cur.fetchone()[0]
            cur.execute(f"DELETE FROM {self._table}")
            return count


# ── Factory ──────────────────────────────────────────────────────────────────

_BACKENDS: dict[str, type[MemoryBackend]] = {
    "sqlite": SQLiteBackend,
    "redis": RedisBackend,
    "postgres": PostgresBackend,
    "postgresql": PostgresBackend,
}


def get_backend(name: str = "sqlite", **kwargs: Any) -> MemoryBackend:
    """Factory function to create a memory backend by name.

    Args:
        name: Backend name (sqlite, redis, postgres)
        **kwargs: Backend-specific arguments (path, url, dsn, etc.)

    Returns:
        Configured MemoryBackend instance
    """
    cls = _BACKENDS.get(name.lower())
    if not cls:
        available = ", ".join(sorted(_BACKENDS.keys()))
        raise ValueError(f"Unknown backend '{name}'. Available: {available}")
    return cls(**kwargs)


def list_backends() -> list[str]:
    """Return list of available backend names."""
    return sorted(set(_BACKENDS.keys()))

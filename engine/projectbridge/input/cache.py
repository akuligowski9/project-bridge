"""Local file cache for GitHub API responses.

Stores JSON responses on disk with TTL-based expiry. Cache files are
organized by API path under a platform-appropriate cache directory.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

_DEFAULT_TTL = 3600  # 1 hour


def _cache_dir() -> Path:
    """Return the cache directory, creating it if necessary."""
    d = Path.home() / ".cache" / "projectbridge"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _key(path: str) -> str:
    """Hash an API path to a safe filename."""
    return hashlib.sha256(path.encode()).hexdigest()


def get(path: str, ttl: int = _DEFAULT_TTL) -> object | None:
    """Return cached response for *path*, or None if expired/missing."""
    file = _cache_dir() / f"{_key(path)}.json"
    if not file.is_file():
        return None
    try:
        data = json.loads(file.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    if time.time() - data.get("ts", 0) > ttl:
        return None
    return data.get("body")


def put(path: str, body: object) -> None:
    """Store *body* as the cached response for *path*."""
    file = _cache_dir() / f"{_key(path)}.json"
    try:
        file.write_text(json.dumps({"ts": time.time(), "body": body}))
    except OSError:
        pass  # non-fatal — cache write failures are silent

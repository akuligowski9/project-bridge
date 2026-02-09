"""Tests for projectbridge.input.cache."""

import json
import time
from unittest.mock import patch

from projectbridge.input import cache


class TestCache:
    def test_put_and_get(self, tmp_path):
        with patch.object(cache, "_cache_dir", return_value=tmp_path):
            cache.put("/users/octocat/repos", [{"name": "hello"}])
            result = cache.get("/users/octocat/repos", ttl=3600)
        assert result == [{"name": "hello"}]

    def test_get_missing_returns_none(self, tmp_path):
        with patch.object(cache, "_cache_dir", return_value=tmp_path):
            result = cache.get("/no/such/path", ttl=3600)
        assert result is None

    def test_expired_returns_none(self, tmp_path):
        with patch.object(cache, "_cache_dir", return_value=tmp_path):
            cache.put("/users/octocat/repos", {"data": 1})
            # Manually backdate the timestamp.
            key = cache._key("/users/octocat/repos")
            file = tmp_path / f"{key}.json"
            data = json.loads(file.read_text())
            data["ts"] = time.time() - 7200  # 2 hours ago
            file.write_text(json.dumps(data))

            result = cache.get("/users/octocat/repos", ttl=3600)
        assert result is None

    def test_corrupt_file_returns_none(self, tmp_path):
        with patch.object(cache, "_cache_dir", return_value=tmp_path):
            cache.put("/path", {"x": 1})
            key = cache._key("/path")
            (tmp_path / f"{key}.json").write_text("not json")
            result = cache.get("/path", ttl=3600)
        assert result is None

    def test_different_paths_independent(self, tmp_path):
        with patch.object(cache, "_cache_dir", return_value=tmp_path):
            cache.put("/a", "alpha")
            cache.put("/b", "beta")
            assert cache.get("/a", ttl=3600) == "alpha"
            assert cache.get("/b", ttl=3600) == "beta"

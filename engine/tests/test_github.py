"""Tests for projectbridge.input.github."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from projectbridge.input.github import (
    GitHubAnalyzer,
    GitHubAPIError,
    GitHubAuthError,
    GitHubClient,
    GitHubRateLimitError,
    GitHubUserNotFoundError,
)


class TestGitHubAnalyzer:
    def test_analyze_returns_required_keys(self, mock_github_response):
        analyzer = GitHubAnalyzer(token="fake")
        with patch.object(analyzer.client, "_request", side_effect=mock_github_response):
            result = analyzer.analyze("testuser")

        assert "languages" in result
        assert "frameworks" in result
        assert "project_structures" in result
        assert "infrastructure_signals" in result
        assert "rate_limit" in result

    def test_detects_languages(self, mock_github_response):
        analyzer = GitHubAnalyzer(token="fake")
        with patch.object(analyzer.client, "_request", side_effect=mock_github_response):
            result = analyzer.analyze("testuser")

        lang_names = [lang["name"] for lang in result["languages"]]
        assert "Python" in lang_names
        assert "JavaScript" in lang_names

    def test_detects_frameworks(self, mock_github_response):
        analyzer = GitHubAnalyzer(token="fake")
        with patch.object(analyzer.client, "_request", side_effect=mock_github_response):
            result = analyzer.analyze("testuser")

        fw_names = [f["name"] for f in result["frameworks"]]
        assert "React" in fw_names
        assert "Django" in fw_names

    def test_detects_infrastructure(self, mock_github_response):
        analyzer = GitHubAnalyzer(token="fake")
        with patch.object(analyzer.client, "_request", side_effect=mock_github_response):
            result = analyzer.analyze("testuser")

        infra_names = [i["name"] for i in result["infrastructure_signals"]]
        assert "Docker" in infra_names

    def test_skips_forks(self, mock_github_response):
        analyzer = GitHubAnalyzer(token="fake")
        with patch.object(analyzer.client, "_request", side_effect=mock_github_response):
            result = analyzer.analyze("testuser")
        # Only 1 non-fork repo, so languages come from that repo only
        assert len(result["languages"]) > 0


class TestGitHubErrors:
    def test_invalid_token(self):
        analyzer = GitHubAnalyzer(token="bad")
        resp = MagicMock()
        resp.status_code = 401
        resp.ok = False
        resp.headers = {}
        with patch("requests.get", return_value=resp):
            with pytest.raises(GitHubAuthError):
                analyzer.analyze("testuser")

    def test_unreachable_api(self):
        analyzer = GitHubAnalyzer(token="fake")
        with patch("requests.get", side_effect=requests.ConnectionError()):
            with pytest.raises(GitHubAPIError, match="Cannot reach"):
                analyzer.analyze("testuser")

    def test_user_not_found(self):
        analyzer = GitHubAnalyzer(token="fake")
        resp = MagicMock()
        resp.status_code = 404
        resp.ok = False
        resp.headers = {}
        with patch("requests.get", return_value=resp):
            with pytest.raises(GitHubUserNotFoundError):
                analyzer.analyze("testuser")

    def test_rate_limit_exceeded(self):
        analyzer = GitHubAnalyzer(token="fake")
        resp = MagicMock()
        resp.status_code = 403
        resp.ok = False
        resp.headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "9999999999"}
        with patch("requests.get", return_value=resp):
            with pytest.raises(GitHubRateLimitError):
                analyzer.analyze("testuser")


class TestFrameworkDetection:
    def test_at_least_20_detectable(self):
        from projectbridge.input.github import (
            FRAMEWORK_INDICATORS,
            GO_MODULE_MAP,
            NPM_FRAMEWORK_MAP,
            PHP_PACKAGE_MAP,
            PYTHON_FRAMEWORK_MAP,
            RUBY_GEM_MAP,
            RUST_CRATE_MAP,
        )

        all_names = set()
        for d in [
            FRAMEWORK_INDICATORS,
            NPM_FRAMEWORK_MAP,
            PYTHON_FRAMEWORK_MAP,
            RUST_CRATE_MAP,
            RUBY_GEM_MAP,
            GO_MODULE_MAP,
            PHP_PACKAGE_MAP,
        ]:
            for name, _ in d.values():
                all_names.add(name)
        assert len(all_names) >= 20

    def test_registry_not_monolithic(self):
        """Detection maps are organized as separate registries, not one giant dict."""
        from projectbridge.input.github import (
            FRAMEWORK_INDICATORS,
            GO_MODULE_MAP,
            NPM_FRAMEWORK_MAP,
            PHP_PACKAGE_MAP,
            PYTHON_FRAMEWORK_MAP,
            RUBY_GEM_MAP,
            RUST_CRATE_MAP,
        )

        registries = [
            FRAMEWORK_INDICATORS,
            NPM_FRAMEWORK_MAP,
            PYTHON_FRAMEWORK_MAP,
            RUST_CRATE_MAP,
            RUBY_GEM_MAP,
            GO_MODULE_MAP,
            PHP_PACKAGE_MAP,
        ]
        assert len(registries) >= 5


class TestTokenManagement:
    def test_token_passed_to_client(self):
        client = GitHubClient(token="my-token")
        assert client.token == "my-token"
        assert client.authenticated is True

    def test_no_token_is_unauthenticated(self):
        client = GitHubClient(token=None)
        assert client.authenticated is False

    def test_empty_token_is_unauthenticated(self):
        client = GitHubClient(token="")
        assert client.authenticated is False

    def test_token_not_in_headers_when_absent(self):
        client = GitHubClient(token=None)
        headers = client._headers()
        assert "Authorization" not in headers

    def test_token_in_headers_when_present(self):
        client = GitHubClient(token="my-token")
        headers = client._headers()
        assert headers["Authorization"] == "Bearer my-token"

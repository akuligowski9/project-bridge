"""Tests for the Ollama AI provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from projectbridge.ai.ollama_provider import OllamaProvider, OllamaProviderError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_urlopen(response_body: dict):
    """Return a mock for urllib.request.urlopen that returns the given body."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_body).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


@pytest.fixture()
def provider():
    """Create an OllamaProvider with the server check bypassed."""
    with patch("projectbridge.ai.ollama_provider.OllamaProvider._check_server"):
        return OllamaProvider(model="test-model")


# ---------------------------------------------------------------------------
# Construction & server check
# ---------------------------------------------------------------------------

class TestOllamaProviderInit:
    def test_default_model(self):
        with patch("projectbridge.ai.ollama_provider.OllamaProvider._check_server"):
            p = OllamaProvider()
            assert p._model == "llama3.2"

    def test_custom_model(self):
        with patch("projectbridge.ai.ollama_provider.OllamaProvider._check_server"):
            p = OllamaProvider(model="mistral")
            assert p._model == "mistral"

    def test_server_unreachable_raises(self):
        import urllib.error
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("refused"),
        ):
            with pytest.raises(OllamaProviderError, match="Cannot reach Ollama"):
                OllamaProvider()


# ---------------------------------------------------------------------------
# analyze_context
# ---------------------------------------------------------------------------

class TestAnalyzeContext:
    def test_returns_enriched_context(self, provider):
        mock_resp = _mock_urlopen({
            "message": {"content": json.dumps({"languages": ["Python"], "ai_insight": "focused"})}
        })
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = provider.analyze_context({"languages": ["Python"]})
        assert result["ai_insight"] == "focused"
        assert result["languages"] == ["Python"]

    def test_non_json_response_preserves_context(self, provider):
        mock_resp = _mock_urlopen({
            "message": {"content": "This is not JSON"}
        })
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = provider.analyze_context({"languages": ["Python"]})
        assert result["languages"] == ["Python"]
        assert result["ai_summary"] == "This is not JSON"


# ---------------------------------------------------------------------------
# generate_recommendations
# ---------------------------------------------------------------------------

class TestGenerateRecommendations:
    def test_returns_recommendations_from_dict(self, provider):
        recs = [{"title": "Build a CLI", "description": "desc", "skills_addressed": ["Python"], "estimated_scope": "small"}]
        mock_resp = _mock_urlopen({
            "message": {"content": json.dumps({"recommendations": recs})}
        })
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = provider.generate_recommendations({"missing_skills": []})
        assert len(result) == 1
        assert result[0]["title"] == "Build a CLI"

    def test_returns_recommendations_from_list(self, provider):
        recs = [{"title": "Deploy", "description": "d", "skills_addressed": ["Docker"], "estimated_scope": "medium"}]
        mock_resp = _mock_urlopen({
            "message": {"content": json.dumps(recs)}
        })
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = provider.generate_recommendations({"missing_skills": []})
        assert len(result) == 1

    def test_invalid_json_raises(self, provider):
        mock_resp = _mock_urlopen({
            "message": {"content": "not json at all"}
        })
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(OllamaProviderError, match="invalid JSON"):
                provider.generate_recommendations({"missing_skills": []})

    def test_unexpected_format_raises(self, provider):
        mock_resp = _mock_urlopen({
            "message": {"content": json.dumps("just a string")}
        })
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(OllamaProviderError, match="unexpected response format"):
                provider.generate_recommendations({"missing_skills": []})


# ---------------------------------------------------------------------------
# _chat
# ---------------------------------------------------------------------------

class TestChat:
    def test_sends_correct_payload(self, provider):
        mock_resp = _mock_urlopen({"message": {"content": "ok"}})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            provider._chat("sys prompt", "user msg")
            call_args = mock_open.call_args
            req = call_args[0][0]
            body = json.loads(req.data)
            assert body["model"] == "test-model"
            assert body["stream"] is False
            assert body["format"] == "json"
            assert body["messages"][0]["role"] == "system"
            assert body["messages"][1]["role"] == "user"

    def test_connection_error_raises(self, provider):
        import urllib.error
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("refused"),
        ):
            with pytest.raises(OllamaProviderError, match="Failed to connect"):
                provider._chat("sys", "user")

    def test_empty_response(self, provider):
        mock_resp = _mock_urlopen({"message": {}})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = provider._chat("sys", "user")
            assert result == ""


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegistration:
    def test_ollama_registered(self):
        from projectbridge.ai.provider import get_provider
        with patch("projectbridge.ai.ollama_provider.OllamaProvider._check_server"):
            p = get_provider("ollama", model="test")
            assert isinstance(p, OllamaProvider)

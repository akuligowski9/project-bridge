"""Tests for projectbridge.ai.gemini_provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from projectbridge.ai.gemini_provider import GeminiProvider, GeminiProviderError
from projectbridge.ai.provider import get_provider


class TestGeminiProviderInit:
    def test_missing_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(GeminiProviderError, match="API key not found"):
                GeminiProvider(api_key=None)

    def test_env_key_used(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            with patch("projectbridge.ai.gemini_provider.GeminiProvider._create_client"):
                provider = GeminiProvider()
                assert provider._api_key == "test-key"

    def test_explicit_key_preferred(self):
        with patch("projectbridge.ai.gemini_provider.GeminiProvider._create_client"):
            provider = GeminiProvider(api_key="explicit-key")
            assert provider._api_key == "explicit-key"

    def test_custom_model(self):
        with patch("projectbridge.ai.gemini_provider.GeminiProvider._create_client"):
            provider = GeminiProvider(api_key="test-key", model="gemini-2.5-flash")
            assert provider._model == "gemini-2.5-flash"


class TestGeminiProviderRegistry:
    def test_registered_as_gemini(self):
        with patch("projectbridge.ai.gemini_provider.GeminiProvider._create_client"):
            p = get_provider("gemini", api_key="test-key")
            assert isinstance(p, GeminiProvider)


class TestAnalyzeContext:
    def _make_provider(self):
        with patch("projectbridge.ai.gemini_provider.GeminiProvider._create_client"):
            return GeminiProvider(api_key="test-key")

    def test_enriches_context(self):
        provider = self._make_provider()
        context = {"languages": [{"name": "Python"}]}
        enriched_response = {**context, "ai_insight": "focused"}

        with patch.object(provider, "_chat", return_value=json.dumps(enriched_response)):
            result = provider.analyze_context(context)

        assert result["ai_insight"] == "focused"
        assert result["languages"] == context["languages"]

    def test_preserves_original_fields_on_partial_response(self):
        provider = self._make_provider()
        context = {"languages": [{"name": "Python"}], "frameworks": []}
        partial = {"languages": [{"name": "Python"}], "ai_summary": "Python dev"}

        with patch.object(provider, "_chat", return_value=json.dumps(partial)):
            result = provider.analyze_context(context)

        assert result["frameworks"] == []

    def test_handles_non_json_response(self):
        provider = self._make_provider()
        context = {"languages": [{"name": "Python"}]}

        with patch.object(provider, "_chat", return_value="Not valid JSON"):
            result = provider.analyze_context(context)

        assert result["languages"] == context["languages"]


class TestGenerateRecommendations:
    def _make_provider(self):
        with patch("projectbridge.ai.gemini_provider.GeminiProvider._create_client"):
            return GeminiProvider(api_key="test-key")

    def test_returns_recommendations(self):
        provider = self._make_provider()
        gaps = {"missing_skills": [{"name": "Kubernetes", "category": "infrastructure"}]}
        response = {
            "recommendations": [
                {
                    "title": "Build a K8s deployment pipeline",
                    "description": "Deploy a microservice to Kubernetes.",
                    "skills_addressed": ["Kubernetes"],
                    "estimated_scope": "medium",
                    "skill_context": "Kubernetes is how teams orchestrate containers at scale.",
                }
            ]
        }

        with patch.object(provider, "_chat", return_value=json.dumps(response)):
            result = provider.generate_recommendations(gaps)

        assert len(result) == 1
        assert result[0]["title"] == "Build a K8s deployment pipeline"
        expected = "Kubernetes is how teams orchestrate containers at scale."
        assert result[0]["skill_context"] == expected

    def test_handles_list_response(self):
        provider = self._make_provider()
        gaps = {"missing_skills": []}
        response = [
            {
                "title": "Project A",
                "description": "Description A",
                "skills_addressed": ["Go"],
                "estimated_scope": "small",
                "skill_context": "Go is valued for backend services.",
            }
        ]

        with patch.object(provider, "_chat", return_value=json.dumps(response)):
            result = provider.generate_recommendations(gaps)

        assert len(result) == 1

    def test_invalid_json_raises(self):
        provider = self._make_provider()
        gaps = {"missing_skills": []}

        with patch.object(provider, "_chat", return_value="not json"):
            with pytest.raises(GeminiProviderError, match="invalid JSON"):
                provider.generate_recommendations(gaps)


class TestChatErrors:
    def _make_provider(self):
        with patch("projectbridge.ai.gemini_provider.GeminiProvider._create_client"):
            return GeminiProvider(api_key="test-key")

    def _make_api_error(self, code: int):
        from google.genai import errors

        class _APIError(errors.APIError):
            def __init__(self, code: int) -> None:
                super().__init__("test error", {"error": {"code": code}})
                self.code = code

        return _APIError(code)

    def test_auth_error(self):
        provider = self._make_provider()
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = self._make_api_error(401)
        provider._client = mock_client

        with pytest.raises(GeminiProviderError, match="Invalid Google API key"):
            provider._chat("system", "user")

    def test_rate_limit_error(self):
        provider = self._make_provider()
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = self._make_api_error(429)
        provider._client = mock_client

        with pytest.raises(GeminiProviderError, match="rate limit"):
            provider._chat("system", "user")

    def test_connection_error(self):
        provider = self._make_provider()
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("connection refused")
        provider._client = mock_client

        with pytest.raises(GeminiProviderError, match="Gemini API error"):
            provider._chat("system", "user")


class TestPromptTemplates:
    def test_analyze_context_template_exists(self):
        from pathlib import Path

        path = (
            Path(__file__).parent.parent
            / "projectbridge"
            / "ai"
            / "prompts"
            / "analyze_context.txt"
        )
        assert path.is_file()
        content = path.read_text()
        assert "developer" in content.lower()

    def test_generate_recommendations_template_exists(self):
        from pathlib import Path

        path = (
            Path(__file__).parent.parent
            / "projectbridge"
            / "ai"
            / "prompts"
            / "generate_recommendations.txt"
        )
        assert path.is_file()
        content = path.read_text()
        assert "recommendation" in content.lower()

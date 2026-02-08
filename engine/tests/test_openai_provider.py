"""Tests for projectbridge.ai.openai_provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from projectbridge.ai.openai_provider import OpenAIProvider, OpenAIProviderError
from projectbridge.ai.provider import get_provider


class TestOpenAIProviderInit:
    def test_missing_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(OpenAIProviderError, match="API key not found"):
                OpenAIProvider(api_key=None)

    def test_env_key_used(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            with patch("projectbridge.ai.openai_provider.OpenAIProvider._create_client"):
                provider = OpenAIProvider()
                assert provider._api_key == "sk-test"

    def test_explicit_key_preferred(self):
        with patch("projectbridge.ai.openai_provider.OpenAIProvider._create_client"):
            provider = OpenAIProvider(api_key="sk-explicit")
            assert provider._api_key == "sk-explicit"

    def test_custom_model(self):
        with patch("projectbridge.ai.openai_provider.OpenAIProvider._create_client"):
            provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini")
            assert provider._model == "gpt-4o-mini"


class TestOpenAIProviderRegistry:
    def test_registered_as_openai(self):
        with patch("projectbridge.ai.openai_provider.OpenAIProvider._create_client"):
            p = get_provider("openai", api_key="sk-test")
            assert isinstance(p, OpenAIProvider)


class TestAnalyzeContext:
    def _make_provider(self):
        with patch("projectbridge.ai.openai_provider.OpenAIProvider._create_client"):
            return OpenAIProvider(api_key="sk-test")

    def test_enriches_context(self):
        provider = self._make_provider()
        context = {"languages": [{"name": "Python"}]}
        enriched_response = {
            **context,
            "ai_summary": "Python developer",
            "ai_seniority_signals": ["single language"],
            "ai_tech_depth": {"Python": "intermediate"},
        }

        with patch.object(provider, "_chat", return_value=json.dumps(enriched_response)):
            result = provider.analyze_context(context)

        assert result["ai_summary"] == "Python developer"
        assert result["languages"] == context["languages"]

    def test_preserves_original_fields_on_partial_response(self):
        provider = self._make_provider()
        context = {"languages": [{"name": "Python"}], "frameworks": []}
        # Response that omits "frameworks"
        partial = {"languages": [{"name": "Python"}], "ai_summary": "Python dev"}

        with patch.object(provider, "_chat", return_value=json.dumps(partial)):
            result = provider.analyze_context(context)

        assert result["frameworks"] == []

    def test_handles_non_json_response(self):
        provider = self._make_provider()
        context = {"languages": [{"name": "Python"}]}

        with patch.object(provider, "_chat", return_value="Not valid JSON"):
            result = provider.analyze_context(context)

        assert result["ai_summary"] == "Not valid JSON"
        assert result["languages"] == context["languages"]


class TestGenerateRecommendations:
    def _make_provider(self):
        with patch("projectbridge.ai.openai_provider.OpenAIProvider._create_client"):
            return OpenAIProvider(api_key="sk-test")

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
                }
            ]
        }

        with patch.object(provider, "_chat", return_value=json.dumps(response)):
            result = provider.generate_recommendations(gaps)

        assert len(result) == 1
        assert result[0]["title"] == "Build a K8s deployment pipeline"

    def test_handles_list_response(self):
        provider = self._make_provider()
        gaps = {"missing_skills": []}
        response = [
            {
                "title": "Project A",
                "description": "Description A",
                "skills_addressed": ["Go"],
                "estimated_scope": "small",
            }
        ]

        with patch.object(provider, "_chat", return_value=json.dumps(response)):
            result = provider.generate_recommendations(gaps)

        assert len(result) == 1

    def test_invalid_json_raises(self):
        provider = self._make_provider()
        gaps = {"missing_skills": []}

        with patch.object(provider, "_chat", return_value="not json"):
            with pytest.raises(OpenAIProviderError, match="invalid JSON"):
                provider.generate_recommendations(gaps)


class TestChatErrors:
    def _make_provider(self):
        with patch("projectbridge.ai.openai_provider.OpenAIProvider._create_client"):
            return OpenAIProvider(api_key="sk-test")

    def test_auth_error(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        from openai import AuthenticationError

        mock_client.chat.completions.create.side_effect = AuthenticationError(
            message="Invalid key",
            response=MagicMock(status_code=401),
            body=None,
        )
        provider._client = mock_client

        with pytest.raises(OpenAIProviderError, match="Invalid OpenAI API key"):
            provider._chat("system", "user")

    def test_rate_limit_error(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        from openai import RateLimitError

        mock_client.chat.completions.create.side_effect = RateLimitError(
            message="Rate limited",
            response=MagicMock(status_code=429),
            body=None,
        )
        provider._client = mock_client

        with pytest.raises(OpenAIProviderError, match="rate limit"):
            provider._chat("system", "user")

    def test_connection_error(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        from openai import APIConnectionError

        mock_client.chat.completions.create.side_effect = APIConnectionError(
            request=MagicMock()
        )
        provider._client = mock_client

        with pytest.raises(OpenAIProviderError, match="Could not connect"):
            provider._chat("system", "user")


class TestPromptTemplates:
    def test_analyze_context_template_exists(self):
        from pathlib import Path

        path = Path(__file__).parent.parent / "projectbridge" / "ai" / "prompts" / "analyze_context.txt"
        assert path.is_file()
        content = path.read_text()
        assert "developer" in content.lower()

    def test_generate_recommendations_template_exists(self):
        from pathlib import Path

        path = Path(__file__).parent.parent / "projectbridge" / "ai" / "prompts" / "generate_recommendations.txt"
        assert path.is_file()
        content = path.read_text()
        assert "recommendation" in content.lower()

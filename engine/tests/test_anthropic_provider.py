"""Tests for projectbridge.ai.anthropic_provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from projectbridge.ai.anthropic_provider import AnthropicProvider, AnthropicProviderError
from projectbridge.ai.provider import get_provider


class TestAnthropicProviderInit:
    def test_missing_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(AnthropicProviderError, match="API key not found"):
                AnthropicProvider(api_key=None)

    def test_env_key_used(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}):
            with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
                provider = AnthropicProvider()
                assert provider._api_key == "sk-ant-test"

    def test_explicit_key_preferred(self):
        with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
            provider = AnthropicProvider(api_key="sk-ant-explicit")
            assert provider._api_key == "sk-ant-explicit"

    def test_custom_model(self):
        with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
            provider = AnthropicProvider(api_key="sk-ant-test", model="claude-haiku-4-5-20251001")
            assert provider._model == "claude-haiku-4-5-20251001"


class TestAnthropicProviderRegistry:
    def test_registered_as_anthropic(self):
        with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
            p = get_provider("anthropic", api_key="sk-ant-test")
            assert isinstance(p, AnthropicProvider)


class TestAnalyzeContext:
    def _make_provider(self):
        with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
            return AnthropicProvider(api_key="sk-ant-test")

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
        with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
            return AnthropicProvider(api_key="sk-ant-test")

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
            with pytest.raises(AnthropicProviderError, match="invalid JSON"):
                provider.generate_recommendations(gaps)


class TestChatErrors:
    def _make_provider(self):
        with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
            return AnthropicProvider(api_key="sk-ant-test")

    def test_auth_error(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        from anthropic import AuthenticationError

        mock_client.messages.create.side_effect = AuthenticationError(
            message="Invalid key",
            response=MagicMock(status_code=401),
            body=None,
        )
        provider._client = mock_client

        with pytest.raises(AnthropicProviderError, match="Invalid Anthropic API key"):
            provider._chat("system", "user")

    def test_rate_limit_error(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        from anthropic import RateLimitError

        mock_client.messages.create.side_effect = RateLimitError(
            message="Rate limited",
            response=MagicMock(status_code=429),
            body=None,
        )
        provider._client = mock_client

        with pytest.raises(AnthropicProviderError, match="rate limit"):
            provider._chat("system", "user")

    def test_connection_error(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        from anthropic import APIConnectionError

        mock_client.messages.create.side_effect = APIConnectionError(request=MagicMock())
        provider._client = mock_client

        with pytest.raises(AnthropicProviderError, match="Could not connect"):
            provider._chat("system", "user")


class TestChatResponseParsing:
    def _make_provider(self):
        with patch("projectbridge.ai.anthropic_provider.AnthropicProvider._create_client"):
            return AnthropicProvider(api_key="sk-ant-test")

    def test_extracts_text_from_content_blocks(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = '{"result": "ok"}'

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_client.messages.create.return_value = mock_response
        provider._client = mock_client

        result = provider._chat("system", "user")
        assert result == '{"result": "ok"}'

    def test_empty_content_returns_empty_string(self):
        provider = self._make_provider()

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response
        provider._client = mock_client

        result = provider._chat("system", "user")
        assert result == ""

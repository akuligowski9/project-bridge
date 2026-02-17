"""Tests for the provider_name override in run_analysis()."""

from projectbridge.orchestrator import run_analysis
from projectbridge.schema import AnalysisResult


class TestProviderNameOverride:
    def test_provider_name_none_uses_heuristic(self):
        result = run_analysis(example=True, provider_name="none")
        assert isinstance(result, AnalysisResult)
        assert len(result.recommendations) > 0

    def test_provider_name_overrides_no_ai_false(self):
        # provider_name="none" should force heuristic even when no_ai is False
        result = run_analysis(example=True, no_ai=False, provider_name="none")
        assert isinstance(result, AnalysisResult)

    def test_provider_name_none_matches_no_ai(self):
        result_provider = run_analysis(example=True, provider_name="none")
        result_no_ai = run_analysis(example=True, no_ai=True)
        # Both should produce the same number of recommendations
        assert len(result_provider.recommendations) == len(result_no_ai.recommendations)

    def test_provider_name_takes_precedence_over_no_ai(self):
        # provider_name should take priority over no_ai flag
        result = run_analysis(example=True, no_ai=True, provider_name="none")
        assert isinstance(result, AnalysisResult)
        assert len(result.strengths) > 0

    def test_provider_name_invalid_raises(self):
        try:
            run_analysis(example=True, provider_name="nonexistent")
            assert False, "Should have raised"
        except Exception as exc:
            assert "nonexistent" in str(exc).lower() or "provider" in str(exc).lower()

    def test_no_provider_name_uses_config_default(self):
        # When provider_name is None and no_ai is False, uses config default
        result = run_analysis(example=True, provider_name=None, no_ai=False)
        assert isinstance(result, AnalysisResult)

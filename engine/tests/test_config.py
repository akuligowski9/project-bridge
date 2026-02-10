"""Tests for projectbridge.config.settings."""

import warnings

from projectbridge.config.settings import CONFIG_FILENAME, ProjectBridgeConfig, load_config


class TestDefaults:
    def test_all_defaults(self):
        cfg = ProjectBridgeConfig()
        assert cfg.ai.provider == "none"
        assert cfg.analysis.max_recommendations == 5
        assert cfg.analysis.confidence_threshold == 0.5
        assert cfg.cache.enabled is True
        assert cfg.cache.ttl_seconds == 3600
        assert cfg.export.default_format == "json"

    def test_load_missing_file(self, tmp_path):
        cfg = load_config(tmp_path / "nonexistent.yaml")
        assert cfg.ai.provider == "none"


class TestLoadYaml:
    def test_load_partial(self, tmp_path):
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text("ai:\n  provider: openai\n")
        cfg = load_config(cfg_file)
        assert cfg.ai.provider == "openai"
        assert cfg.cache.enabled is True  # default preserved


class TestUnknownKeys:
    def test_warns_on_unknown(self, tmp_path):
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text("ai:\n  provider: none\ntypo_key: hello\n")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            load_config(cfg_file)
            unknown = [x for x in w if "Unknown configuration key" in str(x.message)]
            assert len(unknown) == 1

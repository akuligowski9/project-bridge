"""ProjectBridge configuration model.

Loads settings from projectbridge.config.yaml and provides typed defaults
so the engine works with no config file present.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

CONFIG_FILENAME = "projectbridge.config.yaml"


class AISettings(BaseModel):
    """AI provider configuration."""

    provider: str = Field(
        default="none",
        description="AI provider to use: 'openai', 'anthropic', 'ollama', or 'none'.",
    )
    ollama_model: str = Field(
        default="llama3",
        description="Model name when using the Ollama provider.",
    )


class AnalysisSettings(BaseModel):
    """Analysis tuning parameters."""

    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for a skill to be considered detected.",
    )
    max_recommendations: int = Field(
        default=5,
        ge=1,
        description="Maximum number of recommendations to generate.",
    )


class CacheSettings(BaseModel):
    """Caching configuration for GitHub API responses."""

    enabled: bool = Field(default=True, description="Whether to cache API responses.")
    ttl_seconds: int = Field(
        default=3600,
        ge=0,
        description="Cache time-to-live in seconds (default: 1 hour).",
    )


class GitHubSettings(BaseModel):
    """GitHub API configuration."""

    token: str | None = Field(
        default=None,
        description="GitHub personal access token. Prefer GITHUB_TOKEN env var.",
    )


class ExportSettings(BaseModel):
    """Export preferences."""

    default_format: str = Field(
        default="json",
        description="Default export format: 'json' or 'markdown'.",
    )


class ProjectBridgeConfig(BaseModel):
    """Top-level configuration model for ProjectBridge.

    Reads from projectbridge.config.yaml. All fields have sensible defaults
    so the engine works with no config file present.
    """

    ai: AISettings = Field(default_factory=AISettings)
    analysis: AnalysisSettings = Field(default_factory=AnalysisSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    export: ExportSettings = Field(default_factory=ExportSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)

    @model_validator(mode="before")
    @classmethod
    def warn_unknown_keys(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        known_top = {"ai", "analysis", "cache", "export", "github"}
        unknown = set(values.keys()) - known_top
        for key in sorted(unknown):
            warnings.warn(
                f"Unknown configuration key '{key}' in {CONFIG_FILENAME}. "
                "This key will be ignored. Check for typos.",
                UserWarning,
                stacklevel=2,
            )
        return {k: v for k, v in values.items() if k in known_top}


def load_config(config_path: Path | None = None) -> ProjectBridgeConfig:
    """Load configuration from a YAML file.

    Args:
        config_path: Explicit path to the config file. If None, looks for
            ``projectbridge.config.yaml`` in the current working directory.

    Returns:
        A validated ProjectBridgeConfig instance. Returns defaults if the
        config file does not exist.
    """
    if config_path is None:
        config_path = Path.cwd() / CONFIG_FILENAME

    if not config_path.is_file():
        return ProjectBridgeConfig()

    raw = yaml.safe_load(config_path.read_text()) or {}
    return ProjectBridgeConfig.model_validate(raw)

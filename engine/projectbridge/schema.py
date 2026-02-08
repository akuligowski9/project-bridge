"""ProjectBridge analysis output schema v1.0.

Defines the contract between the engine and all consumers (CLI, UI, export).
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class SkillCategory(str, Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    INFRASTRUCTURE = "infrastructure"
    TOOL = "tool"
    CONCEPT = "concept"


class EstimatedScope(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Skill(BaseModel):
    """A skill or technology identified during analysis."""

    name: str = Field(description="Skill or technology name (e.g. 'React', 'Docker').")
    category: SkillCategory = Field(description="Broad classification of the skill.")


class Recommendation(BaseModel):
    """An actionable project suggestion that addresses identified skill gaps."""

    title: str = Field(description="Short, actionable project title.")
    description: str = Field(
        description="Detailed explanation of what to build and why it demonstrates the target skills."
    )
    skills_addressed: list[str] = Field(
        max_length=3,
        description="Skills this project demonstrates. Maximum 3 to keep scope manageable.",
    )
    estimated_scope: EstimatedScope = Field(
        description="Relative effort indicator for the recommended project."
    )


class AnalysisResult(BaseModel):
    """Top-level analysis output conforming to schema v1.0."""

    schema_version: Literal["1.0"] = "1.0"
    strengths: list[Skill] = Field(
        description="Skills detected in both the developer context and job requirements.",
    )
    gaps: list[Skill] = Field(
        description="Skills required by the job but missing from the developer context.",
    )
    recommendations: list[Recommendation] = Field(
        description="Actionable project suggestions that address identified skill gaps.",
    )

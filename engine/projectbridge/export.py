"""JSON export and shareable snapshot.

Wraps a completed analysis result with metadata to produce a
self-contained, shareable snapshot file.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from projectbridge import __version__
from projectbridge.schema import AnalysisResult


class Snapshot(BaseModel):
    """A shareable skill-gap snapshot.

    Self-contained file that includes the analysis result plus metadata
    so it is interpretable without the engine running.
    """

    exported_at: str = Field(
        description="ISO 8601 timestamp of when the snapshot was created.",
    )
    engine_version: str = Field(
        description="ProjectBridge engine version that produced the analysis.",
    )
    schema_version: str = Field(
        description="Output schema version.",
    )
    analysis: AnalysisResult = Field(
        description="The complete analysis result.",
    )


def create_snapshot(result: AnalysisResult) -> Snapshot:
    """Wrap an analysis result in a shareable snapshot.

    Args:
        result: A completed analysis result.

    Returns:
        A :class:`Snapshot` with metadata and the analysis result.
    """
    return Snapshot(
        exported_at=datetime.now(timezone.utc).isoformat(),
        engine_version=__version__,
        schema_version=result.schema_version,
        analysis=result,
    )

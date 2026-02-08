"""Tests for projectbridge.export."""

from projectbridge import __version__
from projectbridge.export import Snapshot, create_snapshot
from projectbridge.schema import AnalysisResult


class TestCreateSnapshot:
    def test_snapshot_has_metadata(self):
        result = AnalysisResult(strengths=[], gaps=[], recommendations=[])
        snap = create_snapshot(result)
        assert snap.exported_at
        assert snap.engine_version == __version__
        assert snap.schema_version == "1.0"
        assert snap.analysis == result

    def test_snapshot_roundtrip(self):
        result = AnalysisResult(strengths=[], gaps=[], recommendations=[])
        snap = create_snapshot(result)
        json_str = snap.model_dump_json()
        roundtrip = Snapshot.model_validate_json(json_str)
        assert roundtrip.engine_version == snap.engine_version
        assert roundtrip.schema_version == snap.schema_version
        assert roundtrip.analysis == snap.analysis

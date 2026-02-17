"""Tests for projectbridge.progress."""

import io
import time
from unittest.mock import patch

from projectbridge.progress import Progress


class TestProgressDisabled:
    def test_step_silent_when_disabled(self):
        p = Progress(enabled=False)
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            p.step("test message")
            assert mock_stderr.getvalue() == ""

    def test_spinner_silent_when_disabled(self):
        p = Progress(enabled=False)
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            p.start_spinner("loading...")
            time.sleep(0.05)
            p.stop_spinner()
            assert mock_stderr.getvalue() == ""

    def test_done_silent_when_disabled(self):
        p = Progress(enabled=False)
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            p.done("finished")
            assert mock_stderr.getvalue() == ""


class TestProgressEnabled:
    def test_step_writes_message(self):
        p = Progress(enabled=True)
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            p.step("Analyzing skills...")
            output = mock_stderr.getvalue()
            assert "Analyzing skills..." in output

    def test_done_writes_message(self):
        p = Progress(enabled=True)
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            p.done("Analysis complete.")
            output = mock_stderr.getvalue()
            assert "Analysis complete." in output

    def test_spinner_starts_and_stops(self):
        p = Progress(enabled=True)
        with patch("sys.stderr", new_callable=io.StringIO):
            p.start_spinner("Fetching data...")
            assert p._spinner_thread is not None
            assert p._spinner_thread.is_alive()
            p.stop_spinner()
            assert p._spinner_thread is None

    def test_step_stops_active_spinner(self):
        p = Progress(enabled=True)
        with patch("sys.stderr", new_callable=io.StringIO):
            p.start_spinner("loading...")
            assert p._spinner_thread is not None
            p.step("Next step")
            assert p._spinner_thread is None

    def test_multiple_stop_spinner_is_safe(self):
        p = Progress(enabled=True)
        p.stop_spinner()
        p.stop_spinner()


class TestProgressAutoDetect:
    def test_defaults_to_disabled_in_tests(self):
        p = Progress()
        assert p._enabled is False

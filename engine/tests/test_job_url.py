"""Tests for the job URL fetcher module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from projectbridge.input.job_url import (
    JobURLExtractionError,
    JobURLFetchError,
    fetch_job_text,
)

SAMPLE_HTML = """
<html>
<head><title>Senior Engineer</title></head>
<body>
<nav>Navigation links here</nav>
<main>
<h1>Senior Python Engineer</h1>
<p>We are looking for a Python developer with experience in Django,
REST APIs, Docker, and PostgreSQL. 4+ years of professional experience required.</p>
</main>
<footer>Copyright 2025</footer>
</body>
</html>
"""

EXTRACTED_TEXT = (
    "We are looking for a Python developer with experience in Django, "
    "REST APIs, Docker, and PostgreSQL. 4+ years of professional experience required."
)


class TestFetchJobText:
    @patch("projectbridge.input.job_url.trafilatura.extract")
    @patch("projectbridge.input.job_url.requests.get")
    def test_fetch_valid_url(self, mock_get, mock_extract):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_HTML
        mock_get.return_value = mock_resp
        mock_extract.return_value = EXTRACTED_TEXT

        result = fetch_job_text("https://example.com/jobs/123")

        assert result == EXTRACTED_TEXT
        mock_get.assert_called_once_with(
            "https://example.com/jobs/123",
            timeout=15,
            headers={"User-Agent": "ProjectBridge/0.2.0"},
        )
        mock_extract.assert_called_once_with(SAMPLE_HTML)

    @patch("projectbridge.input.job_url.requests.get")
    def test_fetch_http_error_403(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_get.return_value = mock_resp

        with pytest.raises(JobURLFetchError, match="require login"):
            fetch_job_text("https://example.com/jobs/123")

    @patch("projectbridge.input.job_url.requests.get")
    def test_fetch_http_error_401(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp

        with pytest.raises(JobURLFetchError, match="require login"):
            fetch_job_text("https://example.com/jobs/123")

    @patch("projectbridge.input.job_url.requests.get")
    def test_fetch_http_error_500(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        with pytest.raises(JobURLFetchError, match="HTTP 500"):
            fetch_job_text("https://example.com/jobs/123")

    @patch("projectbridge.input.job_url.requests.get")
    def test_fetch_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout()

        with pytest.raises(JobURLFetchError, match="timed out"):
            fetch_job_text("https://example.com/jobs/123")

    @patch("projectbridge.input.job_url.requests.get")
    def test_fetch_connection_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError()

        with pytest.raises(JobURLFetchError, match="Could not connect"):
            fetch_job_text("https://example.com/jobs/123")

    @patch("projectbridge.input.job_url.trafilatura.extract")
    @patch("projectbridge.input.job_url.requests.get")
    def test_extraction_returns_none(self, mock_get, mock_extract):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html></html>"
        mock_get.return_value = mock_resp
        mock_extract.return_value = None

        with pytest.raises(JobURLExtractionError, match="Could not extract"):
            fetch_job_text("https://example.com/jobs/123")

    @patch("projectbridge.input.job_url.trafilatura.extract")
    @patch("projectbridge.input.job_url.requests.get")
    def test_extraction_returns_empty(self, mock_get, mock_extract):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html></html>"
        mock_get.return_value = mock_resp
        mock_extract.return_value = "   "

        with pytest.raises(JobURLExtractionError, match="Could not extract"):
            fetch_job_text("https://example.com/jobs/123")

    def test_invalid_url_scheme_ftp(self):
        with pytest.raises(JobURLFetchError, match="Invalid URL scheme"):
            fetch_job_text("ftp://example.com/jobs/123")

    def test_invalid_url_scheme_no_scheme(self):
        with pytest.raises(JobURLFetchError, match="Invalid URL scheme"):
            fetch_job_text("example.com/jobs/123")

    @patch("projectbridge.input.job_url.trafilatura.extract")
    @patch("projectbridge.input.job_url.requests.get")
    def test_fetch_result_passes_validation(self, mock_get, mock_extract):
        """Extracted text should pass validate_job_text() without error."""
        from projectbridge.input.validation import validate_job_text

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_HTML
        mock_get.return_value = mock_resp
        mock_extract.return_value = EXTRACTED_TEXT

        result = fetch_job_text("https://example.com/jobs/123")
        validated = validate_job_text(result)
        assert validated == EXTRACTED_TEXT

    @patch("projectbridge.input.job_url.trafilatura.extract")
    @patch("projectbridge.input.job_url.requests.get")
    def test_custom_timeout(self, mock_get, mock_extract):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_HTML
        mock_get.return_value = mock_resp
        mock_extract.return_value = EXTRACTED_TEXT

        fetch_job_text("https://example.com/jobs/123", timeout=30)

        mock_get.assert_called_once_with(
            "https://example.com/jobs/123",
            timeout=30,
            headers={"User-Agent": "ProjectBridge/0.2.0"},
        )

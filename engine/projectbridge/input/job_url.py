"""Fetch and extract job description text from a URL."""

from __future__ import annotations

import requests
import trafilatura


class JobURLError(Exception):
    """Base error for job URL operations."""


class JobURLFetchError(JobURLError):
    """Raised when fetching the URL fails."""


class JobURLExtractionError(JobURLError):
    """Raised when text extraction from HTML fails."""


def fetch_job_text(url: str, *, timeout: int = 15) -> str:
    """Fetch a web page and extract the main text content.

    Args:
        url: Full URL to a job posting page.
        timeout: HTTP request timeout in seconds.

    Returns:
        Extracted plain-text job description.

    Raises:
        JobURLFetchError: On network or HTTP errors.
        JobURLExtractionError: When text extraction yields nothing.
    """
    if not url.startswith(("http://", "https://")):
        raise JobURLFetchError("Invalid URL scheme. Only http:// and https:// URLs are supported.")

    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "ProjectBridge/0.2.0"},
        )
    except requests.Timeout:
        raise JobURLFetchError(
            "Request timed out. The page may be slow or unreachable. "
            "Try pasting the job description text manually."
        )
    except requests.ConnectionError:
        raise JobURLFetchError(
            "Could not connect to the server. Check the URL and try again, "
            "or paste the job description text manually."
        )
    except requests.RequestException as exc:
        raise JobURLFetchError(
            f"Failed to fetch the URL: {exc}. Try pasting the job description text manually."
        )

    if resp.status_code in (401, 403):
        raise JobURLFetchError(
            "This page may require login or blocks automated access. "
            "Try pasting the job description text manually."
        )

    if resp.status_code >= 400:
        raise JobURLFetchError(
            f"HTTP {resp.status_code} error fetching the page. "
            "Try pasting the job description text manually."
        )

    text = trafilatura.extract(resp.text)

    if not text or not text.strip():
        raise JobURLExtractionError(
            "Could not extract job description text from this page. "
            "The page may use dynamic loading or require JavaScript. "
            "Try pasting the job description text manually."
        )

    return text

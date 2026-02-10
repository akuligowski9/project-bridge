"""CLI progress output.

Displays stage announcements to stderr during long-running operations.
Automatically suppresses output when stderr is not a TTY (piped contexts).
"""

from __future__ import annotations

import sys
import threading


class Progress:
    """Simple progress reporter that writes to stderr.

    Silent when stderr is not a TTY, ensuring JSON output on stdout is
    never polluted.
    """

    def __init__(self, enabled: bool | None = None) -> None:
        if enabled is None:
            enabled = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
        self._enabled = enabled
        self._spinner_thread: threading.Thread | None = None
        self._spinner_stop = threading.Event()

    def step(self, message: str) -> None:
        """Announce a pipeline stage."""
        if not self._enabled:
            return
        self._stop_spinner()
        sys.stderr.write(f"\r\033[K  {message}\n")
        sys.stderr.flush()

    def start_spinner(self, message: str) -> None:
        """Start a spinner with a message. Call stop_spinner() when done."""
        if not self._enabled:
            return
        self._stop_spinner()
        self._spinner_stop.clear()
        self._spinner_thread = threading.Thread(target=self._spin, args=(message,), daemon=True)
        self._spinner_thread.start()

    def _stop_spinner(self) -> None:
        if self._spinner_thread is not None:
            self._spinner_stop.set()
            self._spinner_thread.join(timeout=2)
            self._spinner_thread = None
            sys.stderr.write("\r\033[K")
            sys.stderr.flush()

    def stop_spinner(self) -> None:
        """Stop the active spinner."""
        self._stop_spinner()

    def done(self, message: str = "Done.") -> None:
        """Final message."""
        if not self._enabled:
            return
        self._stop_spinner()
        sys.stderr.write(f"\r\033[K  {message}\n")
        sys.stderr.flush()

    def _spin(self, message: str) -> None:
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not self._spinner_stop.is_set():
            frame = frames[i % len(frames)]
            sys.stderr.write(f"\r\033[K  {frame} {message}")
            sys.stderr.flush()
            i += 1
            self._spinner_stop.wait(0.1)

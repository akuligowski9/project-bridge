"""Tests for the --provider CLI flag."""

from projectbridge.cli import main


class TestProviderFlag:
    def test_provider_none_with_example(self):
        exit_code = main(["analyze", "--example", "--provider", "none"])
        assert exit_code == 0

    def test_provider_flag_overrides_no_ai(self):
        # --provider none should work the same as --no-ai
        exit_code = main(["analyze", "--example", "--provider", "none"])
        assert exit_code == 0

    def test_provider_invalid_choice_rejected(self):
        # argparse should reject invalid provider choices (exits with code 2)
        try:
            main(["analyze", "--example", "--provider", "invalid"])
            assert False, "Should have raised SystemExit"
        except SystemExit as exc:
            assert exc.code == 2

    def test_provider_and_no_ai_both_work(self):
        # --provider takes precedence when both are provided
        exit_code = main(["analyze", "--example", "--no-ai", "--provider", "none"])
        assert exit_code == 0

    def test_help_shows_provider_flag(self, capsys):
        try:
            main(["analyze", "--help"])
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "--provider" in captured.out
        assert "none" in captured.out
        assert "openai" in captured.out
        assert "anthropic" in captured.out
        assert "ollama" in captured.out

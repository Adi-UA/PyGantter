"""Tests for terminal-formatting helpers."""

from pygantter.utils import format_error, format_success, format_warning


def test_format_helpers_tag_messages():
    assert "[ERROR]" in format_error("boom")
    assert "[WARNING]" in format_warning("careful")
    assert "[OK]" in format_success("done")

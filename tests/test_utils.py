import pytest

from pygantter.utils import format_error, format_warning, progress_bar


def test_format_error_and_warning():
    err = format_error("Test error")
    warn = format_warning("Test warning")
    assert "[ERROR]" in err
    assert "[WARNING]" in warn


def test_progress_bar_iterates():
    items = [1, 2, 3]
    out = list(progress_bar(items, desc="Testing"))
    assert out == items
    out = list(progress_bar(items, desc="Testing"))
    assert out == items

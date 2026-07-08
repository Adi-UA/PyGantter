"""Tests for output format resolution and file writing."""

import os
from datetime import datetime, timedelta

import pytest

from pygantter.chart import create_gantt_chart
from pygantter.exceptions import InputFormatError
from pygantter.image import resolve_format, save_chart_image
from pygantter.models import Task

from .conftest import requires_png


def _fig():
    base = datetime(2025, 1, 1)
    return create_gantt_chart(
        [Task("A", base, base + timedelta(days=2))], show_today=False
    )


def test_resolve_format_from_extension():
    assert resolve_format("out.png", None) == "png"
    assert resolve_format("out.HTML", None) == "html"


def test_resolve_format_override_wins():
    assert resolve_format("out.png", "svg") == "svg"


def test_resolve_format_unsupported_raises():
    with pytest.raises(InputFormatError):
        resolve_format("out.gif", None)


@requires_png
def test_save_png(tmp_path):
    out = tmp_path / "gantt.png"
    save_chart_image(_fig(), str(out))
    assert os.path.exists(out) and out.stat().st_size > 0


def test_save_html(tmp_path):
    out = tmp_path / "gantt.html"
    save_chart_image(_fig(), str(out))
    assert os.path.exists(out) and out.stat().st_size > 0

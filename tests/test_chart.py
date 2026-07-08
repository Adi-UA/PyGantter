"""Tests for figure construction and feature overlays."""

from datetime import datetime, timedelta

import plotly.graph_objs as go

from pygantter.chart import create_gantt_chart
from pygantter.models import Task
from pygantter.themes import get_theme


def _project():
    base = datetime(2025, 1, 1)
    return [
        Task("Design", base, base + timedelta(days=4), group="Plan", progress=1.0),
        Task(
            "Build",
            base + timedelta(days=4),
            base + timedelta(days=10),
            dependencies=["Design"],
            group="Dev",
            progress=0.5,
        ),
        Task(
            "Ship",
            base + timedelta(days=10),
            base + timedelta(days=10),
            dependencies=["Build"],
            group="Dev",
        ),
    ]


def test_returns_figure_with_bars():
    fig = create_gantt_chart(_project(), title="T")
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "T"
    assert any(t.type == "bar" for t in fig.data)


def test_today_line_present_and_toggle():
    with_today = create_gantt_chart(_project(), show_today=True)
    without = create_gantt_chart(_project(), show_today=False)
    assert len(with_today.layout.shapes) > len(without.layout.shapes)


def test_milestone_trace_present():
    fig = create_gantt_chart(_project())
    assert any(
        getattr(t, "name", "") == "Milestone" and t.type == "scatter" for t in fig.data
    )


def test_progress_overlay_present_and_toggle():
    with_p = create_gantt_chart(_project(), show_progress=True)
    without = create_gantt_chart(_project(), show_progress=False)
    assert any(getattr(t, "name", "") == "% complete" for t in with_p.data)
    assert not any(getattr(t, "name", "") == "% complete" for t in without.data)


def test_dependency_arrows_present_and_toggle():
    with_dep = create_gantt_chart(_project(), show_dependencies=True, show_today=False)
    without = create_gantt_chart(
        _project(), show_dependencies=False, show_today=False
    )
    arrows = [a for a in with_dep.layout.annotations if a.showarrow]
    assert len(arrows) >= 2  # Design->Build, Build->Ship
    assert not any(a.showarrow for a in without.layout.annotations)


def test_critical_path_outline_applied():
    fig = create_gantt_chart(_project(), show_critical_path=True, show_progress=False)
    widths = []
    for trace in fig.data:
        if trace.type == "bar" and isinstance(trace.marker.line.width, (list, tuple)):
            widths.extend(list(trace.marker.line.width))
    assert any(w and w > 0 for w in widths)


def test_theme_layout_applied():
    theme = get_theme("dark")
    fig = create_gantt_chart(_project(), theme=theme)
    assert fig.layout.plot_bgcolor == theme["background"]
    assert fig.layout.font.color == theme["font"]

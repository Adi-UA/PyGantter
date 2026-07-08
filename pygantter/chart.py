"""Build a Gantt figure from tasks using ``plotly.express.timeline``.

Replaces the deprecated ``figure_factory.create_gantt``. On top of the base
timeline this layers the features that make a Gantt chart useful for planning:
a critical path highlight, milestone markers, a percent-complete overlay,
a "today" line, and dependency arrows.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from .models import Task
from .schedule import compute_schedule
from .themes import Theme, bar_palette, get_theme

_MS_PER_SECOND = 1000.0
_MAIN_BAR_WIDTH = 0.5
_PROGRESS_BAR_WIDTH = 0.24


def create_gantt_chart(
    tasks: Sequence[Task],
    title: str = "Project Timeline",
    theme: Theme | None = None,
    *,
    show_critical_path: bool = True,
    show_dependencies: bool = True,
    show_today: bool = True,
    show_progress: bool = True,
) -> go.Figure:
    """Create a themed Gantt figure.

    Args:
        tasks: Validated tasks to render.
        title: Chart title.
        theme: Color theme mapping; defaults to the light theme.
        show_critical_path: Outline zero-slack tasks in the critical color.
        show_dependencies: Draw arrows from each dependency to its dependent.
        show_today: Draw a vertical marker at the current date.
        show_progress: Overlay a bar showing each task's percent complete.

    Returns:
        A configured :class:`plotly.graph_objs.Figure`.
    """
    if theme is None:
        theme = get_theme("light")

    task_names = [t.name for t in tasks]
    by_name: dict[str, Task] = {t.name: t for t in tasks}
    bars = [t for t in tasks if not t.is_milestone]
    milestones = [t for t in tasks if t.is_milestone]

    critical: set = set()
    if show_critical_path:
        critical = compute_schedule(tasks).critical

    fig = _base_timeline(bars, title, theme)
    _order_axis(fig, task_names)
    _fit_x_axis(fig, tasks)

    if show_critical_path:
        _outline_critical(fig, critical, theme)
    if show_progress:
        _add_progress_overlay(fig, bars, theme)
    if milestones:
        _add_milestones(fig, milestones, critical, theme)
    if show_dependencies:
        _add_dependency_arrows(fig, tasks, by_name, theme)
    if show_today:
        _add_today_line(fig, theme)

    _apply_theme_layout(fig, theme)
    return fig


def _base_timeline(bars: Sequence[Task], title: str, theme: Theme) -> go.Figure:
    """Render the base horizontal bars, colored by group (or task name)."""
    color_by_group = any(t.group for t in bars)
    frame = pd.DataFrame(
        {
            "Task": [t.name for t in bars],
            "Start": [t.start for t in bars],
            "Finish": [t.end for t in bars],
            "Group": [t.group or t.name for t in bars],
            "Resource": [t.resource for t in bars],
        }
    )
    fig = px.timeline(
        frame,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Group",
        color_discrete_sequence=bar_palette(theme),
        title=title,
        hover_data=["Resource"],
    )
    fig.update_traces(width=_MAIN_BAR_WIDTH)
    fig.update_layout(
        legend_title_text="Group" if color_by_group else "Task",
        showlegend=color_by_group,
    )
    return fig


def _order_axis(fig: go.Figure, task_names: Sequence[str]) -> None:
    """Force every task onto the y-axis in input order, first at the top."""
    fig.update_yaxes(
        categoryorder="array", categoryarray=list(reversed(list(task_names)))
    )


def _fit_x_axis(fig: go.Figure, tasks: Sequence[Task]) -> None:
    """Pin the x-axis to the task span so overlays cannot stretch the view.

    Without this, a distant "today" marker would expand the axis and squash
    every bar into a corner. A small padding keeps the first and last bars
    off the chart edges.
    """
    starts = [t.start for t in tasks]
    ends = [t.end for t in tasks]
    if not starts:
        return
    span_days = max((max(ends) - min(starts)).days, 1)
    pad = timedelta(days=max(round(span_days * 0.03), 1))
    fig.update_xaxes(range=[min(starts) - pad, max(ends) + pad])


def _outline_critical(fig: go.Figure, critical: set, theme: Theme) -> None:
    """Add a colored outline to bars whose task is on the critical path."""
    if not critical:
        return
    color = theme["critical"]
    for trace in fig.data:
        if trace.type != "bar" or trace.y is None:
            continue
        widths = [3 if name in critical else 0 for name in trace.y]
        colors = [color] * len(trace.y)
        trace.marker.line.width = widths
        trace.marker.line.color = colors


def _add_progress_overlay(
    fig: go.Figure, bars: Sequence[Task], theme: Theme
) -> None:
    """Overlay a thin inner bar spanning each task's completed fraction."""
    done = [t for t in bars if t.progress > 0]
    if not done:
        return
    lengths_ms = [
        (t.end - t.start).total_seconds() * _MS_PER_SECOND * t.progress for t in done
    ]
    fig.add_trace(
        go.Bar(
            base=[t.start for t in done],
            x=lengths_ms,
            y=[t.name for t in done],
            orientation="h",
            width=_PROGRESS_BAR_WIDTH,
            marker_color=theme["progress"],
            marker_line_width=0,
            opacity=0.55,
            name="% complete",
            hovertemplate="%{y}: complete<extra></extra>",
        )
    )


def _add_milestones(
    fig: go.Figure, milestones: Sequence[Task], critical: set, theme: Theme
) -> None:
    """Draw zero-duration tasks as diamond markers."""
    fig.add_trace(
        go.Scatter(
            x=[t.start for t in milestones],
            y=[t.name for t in milestones],
            mode="markers",
            marker=dict(
                symbol="diamond",
                size=14,
                color=theme["milestone"],
                line=dict(
                    width=[3 if t.name in critical else 0 for t in milestones],
                    color=theme["critical"],
                ),
            ),
            name="Milestone",
            hovertemplate="%{y} (milestone)<extra></extra>",
        )
    )


def _add_dependency_arrows(
    fig: go.Figure,
    tasks: Sequence[Task],
    by_name: dict[str, Task],
    theme: Theme,
) -> None:
    """Draw an arrow from each dependency's end to its dependent's start."""
    for task in tasks:
        for dep_name in task.dependencies:
            pred = by_name.get(dep_name)
            if pred is None:
                continue
            fig.add_annotation(
                x=task.start,
                y=task.name,
                ax=pred.end,
                ay=pred.name,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.1,
                arrowwidth=1.2,
                arrowcolor=theme["arrow"],
                opacity=0.75,
            )


def _add_today_line(fig: go.Figure, theme: Theme) -> None:
    """Draw a dashed vertical line at the current date."""
    fig.add_vline(
        x=datetime.now(),
        line_width=2,
        line_dash="dash",
        line_color=theme["today"],
        annotation_text="Today",
        annotation_position="top",
    )


def _apply_theme_layout(fig: go.Figure, theme: Theme) -> None:
    """Apply background, font, grid, and title colors from the theme."""
    fig.update_layout(
        plot_bgcolor=theme["background"],
        paper_bgcolor=theme["background"],
        font=dict(color=theme["font"]),
        title_font_color=theme["accent"],
        height=600,
        bargap=0.3,
        xaxis=dict(gridcolor=theme["grid"]),
        yaxis=dict(gridcolor=theme["grid"], title=""),
        updatemenus=[],
    )

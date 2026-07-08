"""Tests for dependency ordering and critical-path computation."""

from datetime import datetime, timedelta

import pytest

from pygantter.exceptions import DependencyError
from pygantter.models import Task
from pygantter.schedule import compute_schedule, topological_order


def _task(name, day_start, dur_days, deps=None):
    start = datetime(2025, 1, 1) + timedelta(days=day_start)
    return Task(
        name=name,
        start=start,
        end=start + timedelta(days=dur_days),
        dependencies=deps or [],
    )


def test_topological_order_respects_dependencies():
    deps = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
    order = topological_order(deps)
    assert order.index("A") < order.index("B")
    assert order.index("B") < order.index("D")
    assert order.index("C") < order.index("D")


def test_cycle_detection_raises():
    deps = {"A": ["C"], "B": ["A"], "C": ["B"]}
    with pytest.raises(DependencyError):
        topological_order(deps)


def test_critical_path_diamond():
    # A(2) -> B(3) -> D(1); A -> C(1) -> D. Critical path is A,B,D (length 6).
    tasks = [
        _task("A", 0, 2),
        _task("B", 2, 3, ["A"]),
        _task("C", 2, 1, ["A"]),
        _task("D", 5, 1, ["B", "C"]),
    ]
    schedule = compute_schedule(tasks)
    assert schedule.critical == {"A", "B", "D"}
    assert schedule.project_days == 6
    assert schedule.total_float["C"] == 2


def test_single_task_is_critical():
    schedule = compute_schedule([_task("Solo", 0, 3)])
    assert schedule.critical == {"Solo"}
    assert schedule.project_days == 3


def test_milestone_zero_duration_participates():
    tasks = [
        _task("Work", 0, 4),
        Task(
            name="Ship",
            start=datetime(2025, 1, 5),
            end=datetime(2025, 1, 5),
            dependencies=["Work"],
        ),
    ]
    schedule = compute_schedule(tasks)
    assert "Ship" in schedule.critical
    assert schedule.total_float["Ship"] == 0

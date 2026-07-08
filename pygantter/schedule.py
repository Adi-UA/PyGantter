"""Schedule analysis: dependency ordering and critical-path computation.

The critical path is the chain of dependent tasks with zero slack: any slip
on one of them slips the whole project. This module derives it with the
classic Critical Path Method (CPM) forward/backward pass over task durations.

All functions here are pure (no I/O, no plotting) so they are cheap to test.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass, field

from .exceptions import DependencyError
from .models import Task


@dataclass
class Schedule:
    """Result of analyzing a task list.

    Attributes:
        critical: Names of tasks on the critical path (zero total float).
        total_float: Per-task slack in days. ``0`` means critical.
        project_days: Total project length in days along the critical path.
        order: Task names in a valid topological (dependency-first) order.
    """

    critical: set[str] = field(default_factory=set)
    total_float: dict[str, float] = field(default_factory=dict)
    project_days: float = 0.0
    order: list[str] = field(default_factory=list)


def _successors(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    succ: dict[str, list[str]] = {name: [] for name in dependencies}
    for name, preds in dependencies.items():
        for pred in preds:
            succ[pred].append(name)
    return succ


def topological_order(dependencies: dict[str, list[str]]) -> list[str]:
    """Return task names ordered so every task follows its dependencies.

    Uses Kahn's algorithm. Raises :class:`DependencyError` if the graph
    contains a cycle, naming the tasks still blocked.
    """
    indegree = {name: len(preds) for name, preds in dependencies.items()}
    ready = deque(sorted(name for name, deg in indegree.items() if deg == 0))
    succ = _successors(dependencies)
    order: list[str] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for nxt in succ[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)

    if len(order) != len(dependencies):
        blocked = sorted(set(dependencies) - set(order))
        raise DependencyError(
            "Dependency cycle detected involving: " + ", ".join(blocked)
        )
    return order


def compute_schedule(tasks: Sequence[Task]) -> Schedule:
    """Compute critical path and per-task float for ``tasks``.

    Args:
        tasks: Parsed and validated tasks. Dependency names are assumed to
            reference existing tasks (the parser enforces this).

    Returns:
        A :class:`Schedule` with the critical set, float map, and ordering.

    Raises:
        DependencyError: If the dependency graph contains a cycle.
    """
    duration = {t.name: t.duration_days for t in tasks}
    dependencies = {t.name: list(t.dependencies) for t in tasks}
    order = topological_order(dependencies)
    succ = _successors(dependencies)

    # Forward pass: earliest start/finish.
    earliest_start: dict[str, float] = {}
    earliest_finish: dict[str, float] = {}
    for name in order:
        start = max((earliest_finish[p] for p in dependencies[name]), default=0.0)
        earliest_start[name] = start
        earliest_finish[name] = start + duration[name]

    project_days = max(earliest_finish.values(), default=0.0)

    # Backward pass: latest start/finish.
    latest_start: dict[str, float] = {}
    latest_finish: dict[str, float] = {}
    for name in reversed(order):
        finish = min((latest_start[s] for s in succ[name]), default=project_days)
        latest_finish[name] = finish
        latest_start[name] = finish - duration[name]

    total_float = {
        name: round(latest_start[name] - earliest_start[name], 6) for name in duration
    }
    critical = {name for name, slack in total_float.items() if abs(slack) < 1e-9}

    return Schedule(
        critical=critical,
        total_float=total_float,
        project_days=project_days,
        order=order,
    )

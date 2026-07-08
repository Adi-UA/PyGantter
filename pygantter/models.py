"""Typed domain model for a single Gantt task."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """A single schedulable item on the chart.

    Attributes:
        name: Unique task label. Used as the y-axis category and as the
            identifier that dependencies reference.
        start: Inclusive start datetime.
        end: Inclusive end datetime. Equal to ``start`` for a milestone.
        dependencies: Names of tasks that must finish before this one starts.
        group: Optional grouping label (swimlane / phase). Drives bar color.
        resource: Optional owner or assignee, shown on hover.
        effort: Optional planned effort in days. Used to derive ``end`` when
            an explicit end is not supplied.
        progress: Completion fraction in the closed interval ``[0.0, 1.0]``.
    """

    name: str
    start: datetime
    end: datetime
    dependencies: list[str] = field(default_factory=list)
    group: str = ""
    resource: str = ""
    effort: float | None = None
    progress: float = 0.0

    @property
    def duration_days(self) -> float:
        """Duration in days, never negative. Zero for a milestone."""
        return max((self.end - self.start).total_seconds() / 86_400.0, 0.0)

    @property
    def is_milestone(self) -> bool:
        """True when the task has zero duration (a point in time)."""
        return self.end == self.start

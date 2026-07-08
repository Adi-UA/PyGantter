"""Canonical column names for PyGantter input files.

A single source of truth for the schema keys used across parsing and
rendering. Using an ``Enum`` avoids magic strings and typo bugs.
"""

from __future__ import annotations

from enum import Enum


class TaskField(str, Enum):
    """Recognized columns in a task input file.

    ``str`` subclassing lets these members be used directly as dictionary
    keys and pandas column labels without ``.value`` lookups.
    """

    TASK = "Task"
    START = "Start"
    END = "End"
    EFFORT = "Effort"
    RESOURCE = "Resource"
    DEPENDENCIES = "Dependencies"
    GROUP = "Group"
    PROGRESS = "Progress"

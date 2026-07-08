"""Read and validate task files (CSV, TSV, JSON) into :class:`Task` objects."""

from __future__ import annotations

import json
import math
import os
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd
from dateutil import parser as date_parser

from .enums import TaskField
from .exceptions import (
    DateParseError,
    DependencyError,
    InputFormatError,
    ValidationError,
)
from .models import Task
from .schedule import topological_order

_CSV_EXTS = {".csv": ",", ".tsv": "\t"}


def parse_date(value: Any) -> datetime:
    """Parse a date from many common formats (ISO 8601, US, written).

    Accepts ``datetime``/``date`` instances unchanged. Delegates string
    parsing to ``python-dateutil`` so ``2025-10-01``, ``10/01/2025`` and
    ``Oct 1 2025`` all work.

    Raises:
        DateParseError: If ``value`` cannot be interpreted as a date.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    text = str(value).strip()
    if not text:
        raise DateParseError("Empty date value.")
    try:
        return date_parser.parse(text)
    except (ValueError, OverflowError, TypeError) as exc:
        raise DateParseError(f"Invalid date value: {value!r}") from exc


def _parse_progress(value: Any) -> float:
    """Normalize a progress value to a fraction in ``[0.0, 1.0]``.

    Accepts fractions (``0.5``), percentages (``50`` or ``"50%"``), and blanks.
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return 0.0
    text = str(value).strip().rstrip("%")
    if not text:
        return 0.0
    try:
        number = float(text)
    except ValueError as exc:
        raise ValidationError(f"Invalid progress value: {value!r}") from exc
    if number > 1.0:
        number /= 100.0
    return min(max(number, 0.0), 1.0)


def _read_records(file_path: str) -> list[dict[str, Any]]:
    """Load raw dict records from a supported file, before normalization."""
    if not os.path.exists(file_path):
        raise InputFormatError(f"Input file does not exist: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    if ext in _CSV_EXTS:
        frame = pd.read_csv(file_path, sep=_CSV_EXTS[ext])
        return frame.to_dict(orient="records")
    if ext == ".json":
        with open(file_path, encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise InputFormatError("JSON input must be a list of task objects.")
        return data
    raise InputFormatError(
        f"Unsupported file extension {ext!r}. Use .csv, .tsv, or .json."
    )


def _split_dependencies(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _build_task(record: dict[str, Any], row: int) -> Task:
    """Construct a single :class:`Task` from a raw record."""
    name = record.get(TaskField.TASK)
    if name is None or str(name).strip() == "":
        raise ValidationError(f"Row {row}: missing required '{TaskField.TASK}'.")
    name = str(name).strip()

    if record.get(TaskField.START) in (None, ""):
        raise ValidationError(f"Task {name!r}: missing required '{TaskField.START}'.")
    start = parse_date(record[TaskField.START])

    effort_raw = record.get(TaskField.EFFORT)
    effort = None
    if effort_raw not in (None, "") and not (
        isinstance(effort_raw, float) and math.isnan(effort_raw)
    ):
        try:
            effort = float(effort_raw)
        except ValueError as exc:
            raise ValidationError(
                f"Task {name!r}: invalid '{TaskField.EFFORT}' value {effort_raw!r}."
            ) from exc

    end_raw = record.get(TaskField.END)
    if end_raw not in (None, "") and not (
        isinstance(end_raw, float) and math.isnan(end_raw)
    ):
        end = parse_date(end_raw)
    elif effort is not None:
        end = start + timedelta(days=effort)
    else:
        raise ValidationError(
            f"Task {name!r}: needs an '{TaskField.END}' or an '{TaskField.EFFORT}'."
        )

    if end < start:
        raise ValidationError(
            f"Task {name!r}: end ({end.date()}) is before start ({start.date()})."
        )

    return Task(
        name=name,
        start=start,
        end=end,
        dependencies=_split_dependencies(record.get(TaskField.DEPENDENCIES)),
        group=str(record.get(TaskField.GROUP) or "").strip(),
        resource=str(record.get(TaskField.RESOURCE) or "").strip(),
        effort=effort,
        progress=_parse_progress(record.get(TaskField.PROGRESS)),
    )


def _validate_dependencies(tasks: Sequence[Task]) -> None:
    """Ensure every dependency references an existing, non-self task."""
    names = {t.name for t in tasks}
    for task in tasks:
        for dep in task.dependencies:
            if dep == task.name:
                raise DependencyError(f"Task {task.name!r} depends on itself.")
            if dep not in names:
                raise DependencyError(
                    f"Task {task.name!r} depends on unknown task {dep!r}."
                )


def build_tasks(records: Sequence[dict[str, Any]]) -> list[Task]:
    """Normalize raw records into validated tasks."""
    if not records:
        raise ValidationError("Input contains no tasks.")
    tasks = [_build_task(record, row=i + 1) for i, record in enumerate(records)]
    duplicates = _duplicate_names(tasks)
    if duplicates:
        raise ValidationError(
            "Duplicate task names are not allowed: " + ", ".join(sorted(duplicates))
        )
    _validate_dependencies(tasks)
    # Reject dependency cycles here so validation is a property of the data,
    # not of any render flag. topological_order raises DependencyError on a
    # cycle; the ordering it returns is recomputed later by the scheduler.
    topological_order({t.name: list(t.dependencies) for t in tasks})
    return tasks


def _duplicate_names(tasks: Sequence[Task]) -> set:
    seen: set = set()
    dupes: set = set()
    for task in tasks:
        if task.name in seen:
            dupes.add(task.name)
        seen.add(task.name)
    return dupes


def read_input(file_path: str) -> list[Task]:
    """Read a task file and return validated :class:`Task` objects."""
    return build_tasks(_read_records(file_path))

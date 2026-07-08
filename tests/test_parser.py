"""Tests for input parsing, normalization, and validation."""

import json
from datetime import datetime

import pytest

from pygantter.enums import TaskField
from pygantter.exceptions import (
    DateParseError,
    DependencyError,
    InputFormatError,
    ValidationError,
)
from pygantter.parser import build_tasks, parse_date, read_input


def test_parse_date_iso_and_us_and_written():
    assert parse_date("2025-10-05") == datetime(2025, 10, 5)
    assert parse_date("10/05/2025") == datetime(2025, 10, 5)
    assert parse_date("Oct 5 2025") == datetime(2025, 10, 5)


def test_parse_date_passthrough_datetime():
    dt = datetime(2025, 1, 1)
    assert parse_date(dt) is dt


def test_parse_date_invalid_raises():
    with pytest.raises(DateParseError):
        parse_date("not-a-date")
    with pytest.raises(DateParseError):
        parse_date("")


def test_effort_derives_end_when_end_missing():
    tasks = build_tasks(
        [{TaskField.TASK: "A", TaskField.START: "2025-01-01", TaskField.EFFORT: 4}]
    )
    assert tasks[0].end == datetime(2025, 1, 5)
    assert tasks[0].duration_days == 4


def test_missing_task_name_raises():
    with pytest.raises(ValidationError):
        build_tasks([{TaskField.START: "2025-01-01", TaskField.END: "2025-01-02"}])


def test_missing_start_raises():
    with pytest.raises(ValidationError):
        build_tasks([{TaskField.TASK: "A", TaskField.END: "2025-01-02"}])


def test_end_without_effort_raises():
    with pytest.raises(ValidationError):
        build_tasks([{TaskField.TASK: "A", TaskField.START: "2025-01-01"}])


def test_end_before_start_raises():
    with pytest.raises(ValidationError):
        build_tasks(
            [{TaskField.TASK: "A", TaskField.START: "2025-01-05", TaskField.END: "2025-01-01"}]
        )


def test_duplicate_names_raise():
    rows = [
        {TaskField.TASK: "A", TaskField.START: "2025-01-01", TaskField.END: "2025-01-02"},
        {TaskField.TASK: "A", TaskField.START: "2025-01-03", TaskField.END: "2025-01-04"},
    ]
    with pytest.raises(ValidationError):
        build_tasks(rows)


def test_unknown_dependency_raises():
    with pytest.raises(DependencyError):
        build_tasks(
            [
                {
                    TaskField.TASK: "A",
                    TaskField.START: "2025-01-01",
                    TaskField.END: "2025-01-02",
                    TaskField.DEPENDENCIES: "Ghost",
                }
            ]
        )


def test_dependency_cycle_raises():
    def row(name, dep):
        return {
            TaskField.TASK: name,
            TaskField.START: "2025-01-01",
            TaskField.END: "2025-01-02",
            TaskField.DEPENDENCIES: dep,
        }

    with pytest.raises(DependencyError):
        build_tasks([row("A", "B"), row("B", "A")])


def test_self_dependency_raises():
    with pytest.raises(DependencyError):
        build_tasks(
            [
                {
                    TaskField.TASK: "A",
                    TaskField.START: "2025-01-01",
                    TaskField.END: "2025-01-02",
                    TaskField.DEPENDENCIES: "A",
                }
            ]
        )


def test_progress_normalization_percent_and_fraction():
    def row(name, progress):
        return {
            TaskField.TASK: name,
            TaskField.START: "2025-01-01",
            TaskField.END: "2025-01-02",
            TaskField.PROGRESS: progress,
        }

    tasks = build_tasks([row("A", "50%"), row("B", 0.25), row("C", 200)])
    assert tasks[0].progress == 0.5
    assert tasks[1].progress == 0.25
    assert tasks[2].progress == 1.0  # clamped


def test_dependencies_split_from_string():
    tasks = build_tasks(
        [
            {TaskField.TASK: "A", TaskField.START: "2025-01-01", TaskField.END: "2025-01-02"},
            {TaskField.TASK: "B", TaskField.START: "2025-01-01", TaskField.END: "2025-01-02"},
            {
                TaskField.TASK: "C",
                TaskField.START: "2025-01-03",
                TaskField.END: "2025-01-04",
                TaskField.DEPENDENCIES: "A, B",
            },
        ]
    )
    assert tasks[2].dependencies == ["A", "B"]


def test_empty_input_raises():
    with pytest.raises(ValidationError):
        build_tasks([])


def test_read_input_json(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps(
            [{"Task": "A", "Start": "2025-01-01", "End": "2025-01-02"}]
        )
    )
    tasks = read_input(str(path))
    assert len(tasks) == 1 and tasks[0].name == "A"


def test_read_input_csv(tmp_path):
    path = tmp_path / "tasks.csv"
    path.write_text("Task,Start,End\nA,2025-01-01,2025-01-02\n")
    tasks = read_input(str(path))
    assert tasks[0].end == datetime(2025, 1, 2)


def test_read_input_missing_file_raises():
    with pytest.raises(InputFormatError):
        read_input("does_not_exist.csv")


def test_read_input_bad_extension_raises(tmp_path):
    path = tmp_path / "tasks.txt"
    path.write_text("nope")
    with pytest.raises(InputFormatError):
        read_input(str(path))

import pytest

from pygantter.enums import TaskField
from pygantter.parser import normalize_record, parse_date


def test_parse_date_valid_formats():
    assert parse_date("10/01/2025").year == 2025
    assert parse_date("10/01/2025").month == 10
    assert parse_date("10/01/2025").day == 1


def test_parse_date_invalid_format():
    with pytest.raises(ValueError):
        parse_date("2025.10.01")


def test_normalize_record_basic():
    record = {
        TaskField.TASK: "Design",
        TaskField.START: "10/01/2025",
        TaskField.END: "10/05/2025",
        TaskField.EFFORT: "5",
        TaskField.DEPENDENCIES: "Develop,Test",
    }
    norm = normalize_record(record)
    assert norm[TaskField.TASK] == "Design"
    assert norm[TaskField.EFFORT] == 5
    assert norm[TaskField.DEPENDENCIES] == ["Develop", "Test"]
    assert norm[TaskField.EFFORT] == 5
    assert norm[TaskField.DEPENDENCIES] == ["Develop", "Test"]

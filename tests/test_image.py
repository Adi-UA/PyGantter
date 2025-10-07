import os

import pytest

from pygantter.chart import create_gantt_chart
from pygantter.enums import TaskField
from pygantter.image import preview_chart, save_chart_image
from pygantter.parser import parse_date


def test_save_and_preview_chart(tmp_path):
    tasks = [
        {
            TaskField.TASK: "Design",
            TaskField.START: "10/01/2025",
            TaskField.END: "10/05/2025",
        }
    ]
    for t in tasks:
        t[TaskField.START] = parse_date(t[TaskField.START])
        t[TaskField.END] = parse_date(t[TaskField.END])
    fig = create_gantt_chart(tasks)
    out_path = tmp_path / "gantt.png"
    save_chart_image(fig, str(out_path), format="png")
    assert os.path.exists(out_path)
    # preview_chart(fig)  # Would open a window; skip in CI

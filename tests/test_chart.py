import pytest

from pygantter.chart import create_gantt_chart
from pygantter.enums import TaskField


def test_create_gantt_chart_basic():
    tasks = [
        {
            TaskField.TASK: "Design",
            TaskField.START: "10/01/2025",
            TaskField.END: "10/05/2025",
            TaskField.RESOURCE: "Alice",
        },
        {
            TaskField.TASK: "Develop",
            TaskField.START: "10/06/2025",
            TaskField.END: "10/20/2025",
            TaskField.RESOURCE: "Bob",
        },
    ]
    from pygantter.parser import parse_date

    for t in tasks:
        t[TaskField.START] = parse_date(t[TaskField.START])
        t[TaskField.END] = parse_date(t[TaskField.END])
    fig = create_gantt_chart(tasks, title="Test Chart")
    assert fig is not None
    assert hasattr(fig, "to_image")


def test_create_gantt_chart_with_themes():
    from pygantter.parser import parse_date
    from pygantter.themes import get_theme

    tasks = [
        {
            TaskField.TASK: "Setup",
            TaskField.START: parse_date("10/01/2025"),
            TaskField.END: parse_date("10/02/2025"),
        }
    ]
    theme_light = get_theme("light")
    theme_dark = get_theme("dark")
    fig_light = create_gantt_chart(tasks, title="Light Theme", theme=theme_light)
    fig_dark = create_gantt_chart(tasks, title="Dark Theme", theme=theme_dark)
    assert fig_light is not None
    assert fig_dark is not None

    # Check theme colors applied
    assert fig_light.layout.plot_bgcolor == theme_light["background"]
    assert fig_light.layout.font.color == theme_light["font"]
    assert fig_light.layout.title.font.color == theme_light["accent"]
    assert fig_light.layout.xaxis.gridcolor == theme_light["grid"]
    assert fig_light.layout.yaxis.gridcolor == theme_light["grid"]

    assert fig_dark.layout.plot_bgcolor == theme_dark["background"]
    assert fig_dark.layout.font.color == theme_dark["font"]
    assert fig_dark.layout.title.font.color == theme_dark["accent"]
    assert fig_dark.layout.xaxis.gridcolor == theme_dark["grid"]
    assert fig_dark.layout.yaxis.gridcolor == theme_dark["grid"]

    # Check bar colors
    def hex_to_rgb_str(hex_color):
        hex_color = hex_color.lstrip("#")
        return f"rgb({int(hex_color[0:2],16)}, {int(hex_color[2:4],16)}, {int(hex_color[4:6],16)})"

    bar_colors = [bar.marker.color for bar in fig_light.data]
    expected_bar = hex_to_rgb_str(theme_light["bar"])
    expected_bar_alt = hex_to_rgb_str(theme_light["bar_alt_1"])
    assert expected_bar in bar_colors or expected_bar_alt in bar_colors


def test_create_gantt_chart_complex_title():
    from pygantter.parser import parse_date
    from pygantter.themes import get_theme

    tasks = [
        {
            TaskField.TASK: "Complex Task",
            TaskField.START: parse_date("10/01/2025"),
            TaskField.END: parse_date("10/05/2025"),
        }
    ]
    fig = create_gantt_chart(tasks, title="Complex Timeline", theme=get_theme("light"))
    assert fig.layout.title.text == "Complex Timeline"

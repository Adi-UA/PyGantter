from typing import Any, Dict, List, Optional

import plotly.figure_factory as ff

from .enums import TaskField


def create_gantt_chart(
    tasks: List[Dict[str, Any]],
    title: str = "Project Timeline",
    theme: Optional[Dict[str, str]] = None,
) -> "plotly.graph_objs._figure.Figure":
    """
    Create a Gantt chart using Plotly, applying the provided theme for colors.
    """
    if theme is None:
        from .themes import get_theme

        theme = get_theme("light")

    chart_data = []
    bar_keys = ["bar"] + [f"bar_alt_{i}" for i in range(1, 10)]
    color_list = [theme[k] for k in bar_keys if k in theme]
    for idx, t in enumerate(tasks):
        bar_color = color_list[idx % len(color_list)]
        chart_data.append(
            {
                "Task": t[TaskField.TASK],
                "Start": t[TaskField.START],
                "Finish": t[TaskField.END],
                "Group": t.get(TaskField.GROUP, ""),
                "Resource": t.get(TaskField.RESOURCE, ""),
                "Color": bar_color,
            }
        )

    # Assign bar colors for groups
    groups = [d["Group"] for d in chart_data]
    unique_groups = [g for g in dict.fromkeys(groups) if g]
    bar_keys = ["bar"] + [f"bar_alt_{i}" for i in range(1, 10)]
    color_list = [theme[k] for k in bar_keys if k in theme]
    # Cycle colors if more groups than colors
    colors_for_groups = [
        color_list[i % len(color_list)] for i in range(len(unique_groups))
    ] or color_list

    fig = ff.create_gantt(
        chart_data,
        title=title,
        index_col="Group",
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        height=600,
        bar_width=0.2,
        colors=colors_for_groups,
    )

    fig.update_layout(
        legend_title_text="Task Group",
        plot_bgcolor=theme["background"],
        paper_bgcolor=theme["background"],
        font=dict(color=theme["font"]),
        title_font_color=theme["accent"],
        xaxis=dict(gridcolor=theme["grid"]),
        yaxis=dict(gridcolor=theme["grid"]),
    )
    # Remove timerange modals and interactive controls
    fig.update_layout(updatemenus=[])
    return fig

from typing import Any

import plotly.graph_objs as go


def save_chart_image(fig: go.Figure, output_path: str, format: str = "png") -> None:
    ext = output_path.split(".")[-1].lower()
    fmt = format if format else ext
    if fmt == "html":
        fig.write_html(output_path, config={"displayModeBar": False})
    else:
        fig.write_image(output_path, format=fmt)


def preview_chart(fig: go.Figure) -> None:
    fig.show()


def preview_chart(fig: go.Figure) -> None:
    fig.show()

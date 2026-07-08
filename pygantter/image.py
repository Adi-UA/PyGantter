"""Render a Plotly figure to an image or HTML file, or preview it."""

from __future__ import annotations

import os

import plotly.graph_objs as go

from .exceptions import InputFormatError

_IMAGE_FORMATS = {"png", "svg", "pdf", "jpg", "jpeg", "webp"}
_SUPPORTED = _IMAGE_FORMATS | {"html"}


def resolve_format(output_path: str, override: str | None) -> str:
    """Determine the output format from an override or the file extension.

    Raises:
        InputFormatError: If the resolved format is unsupported.
    """
    fmt = (override or os.path.splitext(output_path)[1].lstrip(".")).lower()
    if fmt not in _SUPPORTED:
        raise InputFormatError(
            f"Unsupported output format {fmt!r}. "
            f"Use one of: {', '.join(sorted(_SUPPORTED))}."
        )
    return fmt


def save_chart_image(
    fig: go.Figure, output_path: str, format: str | None = None
) -> None:
    """Write ``fig`` to ``output_path`` as an image or interactive HTML."""
    fmt = resolve_format(output_path, format)
    if fmt == "html":
        fig.write_html(output_path, config={"displayModeBar": False})
    else:
        fig.write_image(output_path, format=fmt)


def preview_chart(fig: go.Figure) -> None:
    """Open the figure in the default browser / viewer."""
    fig.show()

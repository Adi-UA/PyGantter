"""Command-line interface for PyGantter."""

from __future__ import annotations

import os

import typer

from . import __version__
from .chart import create_gantt_chart
from .exceptions import PyGantterError
from .image import preview_chart, save_chart_image
from .logging import setup_logger
from .parser import read_input
from .themes import available_themes, get_theme
from .utils import format_error, format_success, format_warning

app = typer.Typer(add_completion=False, help="Convert task files into Gantt charts.")
logger = setup_logger()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pygantter {__version__}")
        raise typer.Exit()


@app.command()
def main(
    input: str = typer.Argument(..., help="Input file (CSV, TSV, or JSON)."),
    output: str = typer.Option(..., "--output", "-o", help="Output file path."),
    title: str = typer.Option("Gantt Chart", help="Chart title."),
    theme: str = typer.Option(
        "light", help=f"Color theme: {', '.join(available_themes())}."
    ),
    format: str | None = typer.Option(
        None, help="Output format (png, svg, pdf, html). Defaults to file extension."
    ),
    no_critical_path: bool = typer.Option(
        False, "--no-critical-path", help="Do not highlight the critical path."
    ),
    no_dependencies: bool = typer.Option(
        False, "--no-dependencies", help="Do not draw dependency arrows."
    ),
    no_today: bool = typer.Option(
        False, "--no-today", help="Do not draw the 'today' marker line."
    ),
    no_progress: bool = typer.Option(
        False, "--no-progress", help="Do not draw percent-complete overlays."
    ),
    preview: bool = typer.Option(False, help="Open the chart before saving."),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite the output file if it exists."
    ),
    _version: bool = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """Read ``input``, render a Gantt chart, and write it to ``output``."""
    try:
        if os.path.exists(output) and not force:
            typer.echo(
                format_warning(
                    f"Output file '{output}' exists. Use --force to overwrite."
                )
            )
            raise typer.Exit(code=1)

        chart_theme = get_theme(theme)
        tasks = read_input(input)
        fig = create_gantt_chart(
            tasks,
            title=title,
            theme=chart_theme,
            show_critical_path=not no_critical_path,
            show_dependencies=not no_dependencies,
            show_today=not no_today,
            show_progress=not no_progress,
        )
        if preview:
            preview_chart(fig)
        save_chart_image(fig, output, format=format)
        typer.echo(format_success(f"Chart saved to {output}"))
    except PyGantterError as exc:
        logger.error(str(exc))
        typer.echo(format_error(str(exc)))
        raise typer.Exit(code=1) from exc


def run() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":
    app()

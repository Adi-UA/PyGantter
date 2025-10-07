import os

import typer

from pygantter.chart import create_gantt_chart
from pygantter.image import preview_chart, save_chart_image
from pygantter.logging import setup_logger
from pygantter.parser import read_input
from pygantter.themes import get_theme
from pygantter.utils import format_error, format_warning

app = typer.Typer()
logger = setup_logger()


@app.command()
def main(
    input: str = typer.Argument(..., help="Input file (CSV, TSV, or JSON)"),
    output: str = typer.Option(..., help="Output file (PNG, SVG, or HTML)"),
    title: str = typer.Option("Gantt Chart", help="Chart title"),
    theme: str = typer.Option("light", help="Color theme"),
    format: str = typer.Argument(None, help="Output format (png, svg, or html)"),
    preview: bool = typer.Option(False, help="Preview chart before saving"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite output file"),
):
    try:
        if not os.path.exists(str(input)):
            typer.echo(format_error(f"Input file '{input}' does not exist."))
            raise typer.Exit(code=1)
        if os.path.exists(output) and not force:
            typer.echo(
                format_warning(
                    f"Output file '{output}' exists. Use --force to overwrite."
                )
            )
            raise typer.Exit(code=1)
        config_data = {}
        tasks = read_input(input)
        chart_theme = get_theme(theme)
        fig = create_gantt_chart(tasks, title=title, theme=chart_theme)
        if preview:
            preview_chart(fig)
        save_chart_image(fig, output, format=format)
        typer.echo(f"Chart saved to {output}")
    except Exception as e:
        logger.error(str(e))
        typer.echo(format_error(str(e)))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
if __name__ == "__main__":
    app()

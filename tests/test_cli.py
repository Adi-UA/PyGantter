"""End-to-end CLI tests via Typer's test runner."""

from typer.testing import CliRunner

from pygantter import __version__
from pygantter.cli import app

from .conftest import requires_png

runner = CliRunner()

_CSV = (
    "Task,Start,End,Dependencies,Group,Progress\n"
    "Design,2025-01-01,2025-01-05,,Plan,100\n"
    "Build,2025-01-05,2025-01-12,Design,Dev,40\n"
)


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


@requires_png
def test_render_png(tmp_path):
    src = tmp_path / "tasks.csv"
    src.write_text(_CSV)
    out = tmp_path / "gantt.png"
    result = runner.invoke(app, [str(src), "-o", str(out)])
    assert result.exit_code == 0, result.stdout
    assert out.exists() and out.stat().st_size > 0


def test_unknown_theme_errors(tmp_path):
    src = tmp_path / "tasks.csv"
    src.write_text(_CSV)
    out = tmp_path / "gantt.png"
    result = runner.invoke(app, [str(src), "-o", str(out), "--theme", "nope"])
    assert result.exit_code == 1
    assert "Unknown theme" in result.stdout


def test_cycle_rejected_even_without_critical_path(tmp_path):
    src = tmp_path / "cycle.csv"
    src.write_text(
        "Task,Start,End,Dependencies\n"
        "A,2025-01-01,2025-01-02,B\n"
        "B,2025-01-02,2025-01-03,A\n"
    )
    out = tmp_path / "gantt.html"  # html needs no export backend
    result = runner.invoke(app, [str(src), "-o", str(out), "--no-critical-path"])
    assert result.exit_code == 1
    assert "cycle" in result.stdout.lower()


def test_missing_input_errors(tmp_path):
    out = tmp_path / "gantt.png"
    result = runner.invoke(app, ["nope.csv", "-o", str(out)])
    assert result.exit_code == 1


def test_refuses_overwrite_without_force(tmp_path):
    src = tmp_path / "tasks.csv"
    src.write_text(_CSV)
    out = tmp_path / "gantt.png"
    out.write_text("existing")
    result = runner.invoke(app, [str(src), "-o", str(out)])
    assert result.exit_code == 1
    assert "force" in result.stdout.lower()

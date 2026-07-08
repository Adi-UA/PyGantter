"""Shared pytest fixtures and capability markers."""

import plotly.graph_objects as go
import pytest


def _png_export_available() -> bool:
    """Return True if static PNG export works (kaleido + a headless Chrome)."""
    try:
        go.Figure().to_image(format="png")
        return True
    except Exception:
        return False


PNG_AVAILABLE = _png_export_available()

requires_png = pytest.mark.skipif(
    not PNG_AVAILABLE,
    reason="PNG export backend (kaleido + Chrome) not available in this environment",
)

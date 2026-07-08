"""Tests for theme lookup and palette extraction."""

import pytest

from pygantter.exceptions import ThemeError
from pygantter.themes import available_themes, bar_palette, get_theme


def test_available_themes_includes_ant_dracula_hyphenated():
    themes = available_themes()
    assert "ant-dracula" in themes
    assert "light" in themes and "dark" in themes


def test_get_theme_unknown_raises():
    with pytest.raises(ThemeError):
        get_theme("ant_dracula")  # underscore is the old bug; must fail now
    with pytest.raises(ThemeError):
        get_theme("totally-fake")


def test_get_theme_returns_feature_colors():
    theme = get_theme("light")
    for key in ("critical", "milestone", "progress", "today", "arrow", "background"):
        assert key in theme


def test_bar_palette_nonempty_and_ordered():
    palette = bar_palette(get_theme("dark"))
    assert palette[0] == get_theme("dark")["bar"]
    assert len(palette) == 10

"""Color themes for charts.

Each theme is a flat mapping of role -> hex color. ``bar`` and ``bar_alt_*``
cycle across task groups; the remaining roles style chart features
(critical path, milestones, progress overlay, today marker, arrows).
"""

from __future__ import annotations

from .exceptions import ThemeError

Theme = dict[str, str]

_BAR_PALETTE = {
    "bar": "#FF1744",
    "bar_alt_1": "#00E676",
    "bar_alt_2": "#2979FF",
    "bar_alt_3": "#FFD600",
    "bar_alt_4": "#D500F9",
    "bar_alt_5": "#FF9100",
    "bar_alt_6": "#00B8D4",
    "bar_alt_7": "#FF4081",
    "bar_alt_8": "#C51162",
    "bar_alt_9": "#76FF03",
}

LIGHT_THEME: Theme = {
    **_BAR_PALETTE,
    "background": "#FFFFFF",
    "font": "#212121",
    "grid": "#E0E0E0",
    "accent": "#FFAB00",
    "critical": "#D50000",
    "milestone": "#212121",
    "progress": "#000000",
    "today": "#455A64",
    "arrow": "#616161",
}

DARK_THEME: Theme = {
    **_BAR_PALETTE,
    "background": "#181818",
    "font": "#FAFAFA",
    "grid": "#424242",
    "accent": "#FFD54F",
    "critical": "#FF5252",
    "milestone": "#FAFAFA",
    "progress": "#FFFFFF",
    "today": "#B0BEC5",
    "arrow": "#BDBDBD",
}

ANT_DRACULA_THEME: Theme = {
    "bar": "#FF79C6",
    "bar_alt_1": "#BD93F9",
    "bar_alt_2": "#50FA7B",
    "bar_alt_3": "#FFB86C",
    "bar_alt_4": "#8BE9FD",
    "bar_alt_5": "#FF5555",
    "bar_alt_6": "#F1FA8C",
    "bar_alt_7": "#6272A4",
    "bar_alt_8": "#44475A",
    "bar_alt_9": "#21222C",
    "background": "#282A36",
    "font": "#F8F8F2",
    "grid": "#44475A",
    "accent": "#FF79C6",
    "critical": "#FF5555",
    "milestone": "#F8F8F2",
    "progress": "#282A36",
    "today": "#8BE9FD",
    "arrow": "#6272A4",
}

THEMES: dict[str, Theme] = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
    "ant-dracula": ANT_DRACULA_THEME,
}


def available_themes() -> list[str]:
    """Return theme names in a stable, display-friendly order."""
    return list(THEMES.keys())


def get_theme(name: str) -> Theme:
    """Look up a theme by name.

    Raises:
        ThemeError: If ``name`` is not a known theme. Silent fallback is
            deliberately avoided so typos surface instead of rendering the
            wrong colors.
    """
    try:
        return THEMES[name]
    except KeyError:
        raise ThemeError(
            f"Unknown theme {name!r}. Available: {', '.join(available_themes())}."
        ) from None


def bar_palette(theme: Theme) -> list[str]:
    """Return the ordered list of group-bar colors defined by ``theme``."""
    keys = ["bar"] + [f"bar_alt_{i}" for i in range(1, 10)]
    return [theme[k] for k in keys if k in theme]

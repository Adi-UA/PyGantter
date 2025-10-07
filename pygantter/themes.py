from typing import Dict

LIGHT_THEME: Dict[str, str] = {
    "background": "#FFFFFF",
    "bar": "#FF1744",  # Vibrant Red
    "bar_alt_1": "#00E676",  # Vibrant Green
    "bar_alt_2": "#2979FF",  # Vibrant Blue
    "bar_alt_3": "#FFD600",  # Vibrant Yellow
    "bar_alt_4": "#D500F9",  # Vibrant Purple
    "bar_alt_5": "#FF9100",  # Vibrant Orange
    "bar_alt_6": "#00B8D4",  # Vibrant Cyan
    "bar_alt_7": "#FF4081",  # Vibrant Pink
    "bar_alt_8": "#C51162",  # Vibrant Magenta
    "bar_alt_9": "#76FF03",  # Vibrant Lime
    "font": "#212121",
    "grid": "#E0E0E0",
    "accent": "#FFAB00",
}

DARK_THEME: Dict[str, str] = {
    "background": "#181818",
    "bar": "#FF1744",  # Vibrant Red
    "bar_alt_1": "#00E676",  # Vibrant Green
    "bar_alt_2": "#2979FF",  # Vibrant Blue
    "bar_alt_3": "#FFD600",  # Vibrant Yellow
    "bar_alt_4": "#D500F9",  # Vibrant Purple
    "bar_alt_5": "#FF9100",  # Vibrant Orange
    "bar_alt_6": "#00B8D4",  # Vibrant Cyan
    "bar_alt_7": "#FF4081",  # Vibrant Pink
    "bar_alt_8": "#C51162",  # Vibrant Magenta
    "bar_alt_9": "#76FF03",  # Vibrant Lime
    "font": "#FAFAFA",
    "grid": "#424242",
    "accent": "#FFD54F",
}

ANT_DRACULA_THEME: Dict[str, str] = {
    "background": "#282A36",
    "bar": "#FF79C6",  # Pink
    "bar_alt_1": "#BD93F9",  # Purple
    "bar_alt_2": "#50FA7B",  # Green
    "bar_alt_3": "#FFB86C",  # Orange
    "bar_alt_4": "#8BE9FD",  # Cyan
    "bar_alt_5": "#FF5555",  # Red
    "bar_alt_6": "#F1FA8C",  # Yellow
    "bar_alt_7": "#6272A4",  # Dark Blue
    "bar_alt_8": "#44475A",  # Darker Gray
    "bar_alt_9": "#21222C",  # Almost Black
    "font": "#F8F8F2",
    "grid": "#44475A",
    "accent": "#FF79C6",
}

THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
    "ant_dracula": ANT_DRACULA_THEME,
}


def get_theme(name: str) -> Dict[str, str]:
    return THEMES.get(name, LIGHT_THEME)

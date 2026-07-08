"""Regenerate the sample output images committed to the repo.

Run from the repo root:  python scripts/generate_examples.py
"""

from __future__ import annotations

import os

from pygantter.chart import create_gantt_chart
from pygantter.image import save_chart_image
from pygantter.parser import read_input
from pygantter.themes import get_theme

INPUT_DIR = "sample_inputs"
OUTPUT_DIR = "sample_outputs"

EXAMPLES = [
    ("tasks.csv", "tasks_csv"),
    ("tasks.tsv", "tasks_tsv"),
    ("tasks.json", "tasks_json"),
    ("complex.csv", "complex_example"),
]

# (theme key used by the library, token used in output filenames)
THEMES = [("light", "light"), ("dark", "dark"), ("ant-dracula", "ant_dracula")]


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for theme_key, token in THEMES:
        theme = get_theme(theme_key)
        for fname, out_prefix in EXAMPLES:
            tasks = read_input(os.path.join(INPUT_DIR, fname))
            title = f"{out_prefix.replace('_', ' ').title()} ({theme_key} theme)"
            out_path = os.path.join(OUTPUT_DIR, f"{out_prefix}_{token}.png")
            fig = create_gantt_chart(tasks, title=title, theme=theme)
            save_chart_image(fig, out_path, format="png")
            print(f"Generated: {out_path}")

    # Wide hero image for the README.
    hero_tasks = read_input(os.path.join(INPUT_DIR, "tasks.csv"))
    hero = create_gantt_chart(
        hero_tasks, title="PyGantter — Website Launch", theme=get_theme("ant-dracula")
    )
    hero.update_layout(width=1200, height=520)
    hero_path = os.path.join(OUTPUT_DIR, "hero.png")
    save_chart_image(hero, hero_path, format="png")
    print(f"Generated: {hero_path}")


if __name__ == "__main__":
    main()

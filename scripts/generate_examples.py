import os

from pygantter.chart import create_gantt_chart
from pygantter.image import save_chart_image
from pygantter.parser import read_input
from pygantter.themes import get_theme

EXAMPLES = [
    ("tasks.csv", "tasks_csv"),
    ("tasks.tsv", "tasks_tsv"),
    ("tasks.json", "tasks_json"),
    ("complex.csv", "complex_example"),
]

THEMES = ["light", "dark", "ant_dracula"]


def main():
    input_dir = "sample_inputs"
    output_dir = "sample_outputs"
    os.makedirs(output_dir, exist_ok=True)
    for theme_name in THEMES:
        theme = get_theme(theme_name)
        for fname, out_prefix in EXAMPLES:
            input_path = os.path.join(input_dir, fname)
            tasks = read_input(input_path)
            title = (
                f"{out_prefix.replace('_', ' ').title()} ({theme_name.title()} Theme)"
            )
            out_file = f"{out_prefix}_{theme_name}.png"
            out_path = os.path.join(output_dir, out_file)
            fig = create_gantt_chart(tasks, title=title, theme=theme)
            save_chart_image(fig, out_path, format="png")
            print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()

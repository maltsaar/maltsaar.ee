from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from create_website.configuration import DATA_DIRECTORY

env = Environment(
    loader=FileSystemLoader([DATA_DIRECTORY / "templates", DATA_DIRECTORY / "content-templates"]),
    autoescape=select_autoescape(),
    lstrip_blocks=True,
    trim_blocks=True
)

def render_template(page: str, render_path: Path, template_vars: dict) -> None:
    template = env.get_template(f"{page}.html.jinja")

    with render_path.open("w", encoding="utf-8") as f:
        f.write(template.render(template_vars))

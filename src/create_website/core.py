import logging
from pathlib import Path
import shutil
from create_website.pages import create_pages
from create_website.blog import create_blog
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from create_website.configuration import OUTPUT_DIRECTORY, DATA_DIRECTORY, CONFIGURATION_FILE, PYGMENTS_DEFAULT_THEME, toml_to_dict

log = logging.getLogger("create-website")

def create_output_directory() -> None:
    directory = OUTPUT_DIRECTORY

    # If output directory doesn't exist then create it
    if not directory.exists():
        log.debug("Creating output directory")
        directory.mkdir()

    # If output directory contains anything then wipe it
    if any(directory.iterdir()):
        log.debug("Wiping output directory contents")
        shutil.rmtree(directory)
        directory.mkdir()

    # Move ./assets to OUTPUT_DIRECTORY/assets but ignore ./assets/root
    assets_directory = DATA_DIRECTORY / "assets"
    def ignore_root(directory, contents):
        return ["root"] if "root" in contents else []

    shutil.copytree(
        assets_directory, directory / "assets", ignore=ignore_root, dirs_exist_ok=True
    )

    # Move ./assets/root to OUTPUT_DIRECTORY
    if (assets_directory / "root").exists():
        shutil.copytree(
            assets_directory / "root", directory, dirs_exist_ok=True
        )

def generate_pygments_stylesheet(style: str) -> None:
    log.info("Creating pygments stylesheet (%s)", style)

    file_path = OUTPUT_DIRECTORY / "assets/pygments.css"
    try:
        css = HtmlFormatter(style=style).get_style_defs('.highlight')
    except ClassNotFound:
        log.warning("Pygments theme not found. Setting to default value.")
        css = HtmlFormatter(style=PYGMENTS_DEFAULT_THEME).get_style_defs('.highlight')

    file_path.write_text(css)

def check_and_create_blog(blog: dict, global_template_vars: dict) -> None:
    if not blog["generate_blog"]:
        log.info("Skipping blog generation")
        return

    # Set pygments theme
    generate_pygments_stylesheet(blog["pygments_theme"])

    if not blog["generate_rss_feed"]:
        create_blog(global_template_vars)
    else:
        if "rss" not in blog:
            raise KeyError("[blog.rss] is a mandatory section if generate_rss_feed is defined")

        rss_configuration = blog["rss"]
        create_blog(global_template_vars, True, rss_configuration)

def create_website():
    create_output_directory()

    try:
        log.debug(f"Reading and validating {CONFIGURATION_FILE}")
        global_template_vars = toml_to_dict(CONFIGURATION_FILE, "global_template_vars")
        pages = toml_to_dict(CONFIGURATION_FILE, "pages")
        blog = toml_to_dict(CONFIGURATION_FILE, "blog")
    except:
        log.exception("Encountered exception while running toml_to_dict()")
        raise

    try:
        create_pages(pages, global_template_vars)
    except:
        log.exception("Encountered exception while running create_pages()")
        raise

    try:
        check_and_create_blog(blog, global_template_vars)
    except:
        log.exception("Encountered exception while running check_and_create_blog()")

import logging
from pathlib import Path
from datetime import datetime
import re
import configparser
from mistune import create_markdown
from create_website.mistune_override import CustomHTMLRenderer, bootstrap_table
from create_website.jinja import render_template
from create_website.configuration import OUTPUT_DIRECTORY, DATA_DIRECTORY, CONFIGURATION_FILE, toml_to_dict
from feedgen.feed import FeedGenerator
from typing import Optional

log = logging.getLogger("create-website")

def split_markdown(md: str, md_file_path: Path) -> dict:
    # Regex to match the metadata block (between '---' delimiters)
    metadata_pattern = r"^\-\-\-([\s\S]*?)\-\-\-\n"
    metadata_match = re.match(metadata_pattern, md)

    # Parse metadata block
    if not metadata_match:
        error_msg = f"Missing metadata block in markdown ({md_file_path}) content"
        raise ValueError(error_msg)

    metadata_block = metadata_match.group(1).strip()
    md_content = md[len(metadata_match.group(0)):].strip()

    return {
        "metadata_block": metadata_block,
        "md_content": md_content
    }

def get_markdown_metadata(metadata_block: str, md_file_path: Path) -> dict:
    # Convert the parsed metadata into a dictionary
    config = configparser.ConfigParser()
    config.read_string(f"[metadata]\n{metadata_block}")

    metadata = {
        key: value.strip('"') for key, value in config.items(
            "metadata"
        )
    }

    # Check if all required metadata fields are present
    keys_to_check = ["title", "published", "description"]
    if not all(key in metadata for key in keys_to_check):
        raise ValueError(f"One of the following required fields is not present in the metadata block: {keys_to_check}")

    # Create formatted timestamp date
    datetime_object = datetime.fromisoformat(metadata["published"])
    metadata["published_web"] = datetime_object.strftime("%d %b %Y")

    # Create formatted updated timestamp if it exists
    if "updated" in metadata:
        datetime_object = datetime.fromisoformat(metadata["updated"])
        metadata["updated_web"] = datetime_object.strftime("%d %b %Y")

    # Include path in metadata
    metadata["path"] = f"/blog/{md_file_path.stem}"

    return metadata

def create_blog_pages(blog_output_directory: Path, global_template_vars: dict) -> list:
    md_directory = DATA_DIRECTORY / "blog"
    md_list = list(md_directory.glob("*.md"))

    blog_output_directory.mkdir()

    # Render individual blog pages
    metadata_list = []
    for key in md_list:
        log.info("Creating \"%s\"", key)
        md_file_path = Path(key)

        with md_file_path.open(encoding="utf-8") as f:
            md = f.read()

        try:
            split_markdown_list = split_markdown(md, md_file_path)
        except ValueError:
            raise

        md_content = split_markdown_list["md_content"]
        metadata_block = split_markdown_list["metadata_block"]

        try:
            metadata = get_markdown_metadata(metadata_block, md_file_path)
        except ValueError:
            raise

        # Add metadata to metadata dict
        metadata_list.append(metadata)

        # Parse markdown to html
        markdown_parser = create_markdown(
            renderer=CustomHTMLRenderer(), #type: ignore
            plugins=[bootstrap_table] #type: ignore
        )
        html_content = markdown_parser(md_content)

        blog_entry_directory = blog_output_directory / f"{md_file_path.stem}"
        blog_entry_directory.mkdir()
        file_path = blog_entry_directory / "index.html"

        render_template("blog-entry", file_path, {
            "gtv": global_template_vars,
            "tv": {
                "current_page": "blog",
                "metadata": metadata,
                "html_content": html_content
            },
        })

    return metadata_list

def create_blog_index(blog_output_directory: Path, metadata_list: list, global_template_vars: dict) -> None:
    log.info("Creating blog index")

    # Sort by "published" descending
    metadata_list.sort(key=lambda x: datetime.fromisoformat(x["published"]), reverse=True)

    file_path = blog_output_directory / "index.html"
    render_template("blog-index", file_path, {
        "gtv": global_template_vars,
        "tv": {
            "current_page": "blog",
            "metadata_list": metadata_list
        }
    })

def create_rss_feed(blog_output_directory: Path, metadata_list: list, configuration: dict) -> None:
    log.info("Creating RSS feed")

    fg = FeedGenerator()
    # https://feedgen.kiesow.be/api.feed.html
    fg.title(configuration["title"])
    fg.description(configuration["description"])
    fg.language(configuration["language"])
    fg.link(href=f"{configuration["base_url"]}/blog", rel="alternate")

    for key in metadata_list:
        entry = fg.add_entry()

        entry.title(key["title"])
        entry.description(key["description"], True)

        feedgen_link = f"{configuration["base_url"]}{key["path"]}"
        entry.link(href=feedgen_link, rel="alternate")
        entry.guid(feedgen_link, True)

        published_date_object = datetime.fromisoformat(key["published"])
        entry.published(published_date_object)

    fg.rss_file(blog_output_directory / "rss.xml")

def create_blog(global_template_vars: dict, generate_rss_feed: bool = False, rss_configuration: Optional[dict] = None) -> None:
    blog_output_directory = OUTPUT_DIRECTORY / "blog"
    metadata_list = create_blog_pages(blog_output_directory, global_template_vars)
    create_blog_index(blog_output_directory, metadata_list, global_template_vars)

    if not generate_rss_feed:
        log.info("Skipping blog feed generation")
        return

    if rss_configuration is not None:
        create_rss_feed(blog_output_directory, metadata_list, rss_configuration)

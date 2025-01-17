import logging
from create_website.configuration import OUTPUT_DIRECTORY
from create_website.jinja import render_template

log = logging.getLogger("create-website")

def create_pages(pages: dict, global_template_vars: dict) -> None:
    for key in pages:
        log.info("Creating \"%s\"", key)

        template_vars = {}
        template_vars["current_page"] = key
        if "template_vars" in pages[key]:
            template_vars.update(pages[key]["template_vars"])

        log.debug("template_vars: %s", template_vars)

        page_in_root = pages[key].get("root", False)
        if key != "index":
            log.debug(f"page_in_root: %s", page_in_root)

        # if template is "index" or root=True set file path to the root of OUTPUT_DIRECTORY
        if key == "index" or page_in_root:
            file_path = OUTPUT_DIRECTORY / f"{key}.html"
        else:
            directory = OUTPUT_DIRECTORY / f"{key}"
            directory.mkdir()
            file_path = directory / "index.html"

        render_template(key, file_path, {
            "gtv": global_template_vars,
            "tv": template_vars,
        })

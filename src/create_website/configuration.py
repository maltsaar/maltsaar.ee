from pathlib import Path
from os import environ
import tomllib
from cerberus import Validator

CONFIGURATION_FILE = Path("configuration.toml")
OUTPUT_DIRECTORY = Path(environ.get("OUTPUT_LOCATION", "output"))
DATA_DIRECTORY = Path(environ.get("DATA_LOCATION", "./"))

PYGMENTS_DEFAULT_THEME = "zenburn"

def toml_to_dict(path: Path, key: str) -> dict:
    with open(path, "rb") as file:
        toml = tomllib.load(file)

    if key not in toml:
        raise KeyError(f"{key} is a mandatory section in {CONFIGURATION_FILE}")

    if key == "blog":
        return validate_and_return(toml[key])
    elif key == "pages":
        return validate_and_return(toml[key], True)

    return toml[key]

schema_blog = {
    "generate_blog": {
        "type": "boolean",
        "required": True
    },
    'generate_rss_feed': {
        "type": "boolean",
        "default": False
    },
    "pygments_theme": {
        "type": "string",
        "default": PYGMENTS_DEFAULT_THEME
    },
    "rss": {
        "type": "dict",
        "schema": {
            "base_url": {
                "type": "string",
                "regex": r"^https?:\/\/.+",
                "required": True
            },
            "language": {
                "type": "string",
                "minlength": 2,
                "maxlength": 2,
                "required": True
            },
            "title": {
                "type": "string",
                "required": True
            },
            "description": {
                "type": "string",
                "required": True
            },
        },
    },
}

schema_index = {
    "index": {
        "type": "dict",
        "required": True,
        "schema": {
            "template_vars": {
                "type": "dict",
                "allow_unknown": True,
            },
        },
    }
}

schema_generic_page = {
    "generic_page": {
        "type": "dict",
        "schema": {
            "root": {
                "type": "boolean",
                "default": False,
            },
            "template_vars": {
                "type": "dict",
                "allow_unknown": True,
            },
        },
    },
}

def validate_and_return(data: dict, for_pages=False) -> dict:
    if not for_pages:
        validator = Validator(schema_blog) # pyright: ignore
        if not validator.validate(data): # pyright: ignore
            raise ValueError(f"Configuration validation failed: {validator.errors}") # pyright: ignore

        return validator.document # pyright: ignore

    validated_pages = {}
    for page in data:
        if page == "index":
            validator = Validator(schema_index) # pyright: ignore
        else:
            schema = schema_generic_page.copy()
            schema[page] = schema.pop("generic_page")
            validator = Validator(schema) # pyright: ignore

        page_dict = {
            page: data[page]
        }
        if not validator.validate(page_dict): # pyright: ignore
            raise ValueError(f"Configuration validation failed: {validator.errors}") # pyright: ignore

        validated_pages.update(validator.document) # pyright: ignore

    return validated_pages

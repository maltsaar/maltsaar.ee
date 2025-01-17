# maltsaar.ee

My personal website.

## create-website

The website is built with a fairly simple python package I wrote. This might end up going into its own repository in the future.

Features: Jinja templating, Blog (Optional) with RSS, syntax highlighting and markdown support

### Configuration

Configuration sits inside `configuration.toml`.

This is used to configure the blog, define jinja2 template variables and individual web pages.

### Directory structure

| dir | desc |
| - | - |
| assets | Contains static assets for the website (Stylesheets, js, images etc) |
| blog | Contains markdown files. Each one is treated as an individual blog post. |
| templates | Contains jinja2 templates. These are used as base templates for individual pages or for the blog. |
| content-templates | Contains jinja2 templates. Every template in this folder gets treated as an individual page. |
| output | Contains the built website. This folder gets created automatically during runtime. |

### Usage

You can build the website by running the `create_website` script with uv

```shell
uv run create_website
```

#### Usage examples

If you want to test locally you can use pythons built in web server. You can also set `LOG_LEVEL` env var for debugging.

```shell
LOG_LEVEL=DEBUG uv run create_website && python -m http.server 8000 -d output
```

Setting a custom path for data and output

```shell
DATA_LOCATION=data/is/here OUTPUT_LOCATION=build/the/website/here uv run create_website
```

Clean output directory and log file

```shell
uv run clean
```

### Build

You can generate a python3 .whl distributable and install with pip

```shell
uv build
cd dist
pip3 install create_website-0.1.0-py3-none-any.whl
```

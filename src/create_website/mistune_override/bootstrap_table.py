from typing import TYPE_CHECKING
from mistune.plugins import table

if TYPE_CHECKING:
    from mistune.core import BaseRenderer
    from mistune.markdown import Markdown

def bootstrap_table(md: "Markdown") -> None:
    md.block.register('table', table.TABLE_PATTERN, table.parse_table, before='paragraph')
    md.block.register('nptable', table.NP_TABLE_PATTERN, table.parse_nptable, before='paragraph')

    if md.renderer and md.renderer.NAME == 'html':
        # Custom function to add a class element
        md.renderer.register('table', render_table)
        # Everything else calls standard functions in the table module
        md.renderer.register('table_head', table.render_table_head)
        md.renderer.register('table_body', table.render_table_body)
        md.renderer.register('table_row', table.render_table_row)
        md.renderer.register('table_cell', table.render_table_cell)

def render_table(renderer: "BaseRenderer", text: str) -> str:
    return f"<table class=\"table w-auto table-bordered\">\n{text}</table>\n"

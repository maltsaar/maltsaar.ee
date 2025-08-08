from typing import Optional, Any
import re
from mistune import HTMLRenderer
from mistune.util import escape as escape_text
from mistune.util import safe_entity, striptags
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class CustomHTMLRenderer(HTMLRenderer):
    formatter = HtmlFormatter(wrapcode=True)

    # This is for
    # ```
    # ```
    def block_code(self, code: str, info: Optional[str] = None) -> str:
        if info:
            lexer = get_lexer_by_name(info, stripall=True)
            return highlight(code, lexer, self.formatter)
        return f"<pre><code>{escape_text(code)}</code></pre>"

    # This is for
    # ``
    def codespan(self, text: str) -> str:
        return f"<code class=\"highlight p-1 bg-body-secondary rounded user-select-all\">{escape_text(text)}</code>"

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        # https://www.markdownguide.org/extended-syntax/#heading-ids
        # If a heading-id isn't present we create our own from the contents of the heading
        _id = attrs.get('id')
        if _id:
            return f"<h{str(level)} class=\"mt-4\" id=\"{_id}\">{text}</h{str(level)}>\n"
        else:
            # replace all spaces with a hyphen and convert to lowercase
            id_from_text = text.replace(" ", "-").lower()
            # remove all special characters besides hyphens
            id = re.sub("[^a-zA-Z0-9-]+", '', id_from_text)

        # Display <h1> as <h2> and so on because the former is used in the blog title
        level += 1

        heading = f"<h{str(level)} class=\"mt-4\" id=\"{id}\">{text}</h{str(level)}>"

        # Add an underline for h2 because it's the highest heading level
        if level == 2:
            heading = f"{heading}<hr>\n"
        
        return f"{heading}\n"

    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        style = "link-offset-2 link-offset-3-hover link-underline link-underline-opacity-0 link-underline-opacity-75-hover"

        if title:
            title = safe_entity(title)
            return f"<a class=\"{style}\" href=\"{self.safe_url(url)}\" title=\"{title}\">{text}</a>"

        return f"<a class=\"{style}\" href=\"{self.safe_url(url)}\">{text}</a>"

    def image(self, text: str, url: str, title: Optional[str] = None) -> str:
        src = self.safe_url(url)
        alt = escape_text(striptags(text))

        if title:
            title = safe_entity(title)
            return f"<img class=\"img-fluid\" src=\"{src}\" alt=\"{alt}\" title=\"{title}\"/>"

        return f"<img class=\"img-fluid\" src=\"{src}\" alt=\"{alt}\"/>"

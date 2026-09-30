import markdown as md_lib


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown text to styled HTML suitable for rich text editor and Word export."""
    if not markdown_text:
        return ""
    html = md_lib.markdown(
        markdown_text,
        extensions=['tables', 'fenced_code', 'nl2br'],
        output_format='html5'
    )
    return html

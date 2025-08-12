"""WeasyPrint configuration for PDF generation."""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Try to import WeasyPrint, handle gracefully if not installed
try:
    import weasyprint

    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning(
        "WeasyPrint not installed. PDF generation will be unavailable. "
        "Install with: pip install weasyprint"
    )
    weasyprint = None


def get_weasyprint_config() -> Dict[str, str]:
    """Get WeasyPrint configuration for book format."""
    return {
        "page_width": "156mm",
        "page_height": "234mm",
        "margin_top": "20mm",
        "margin_bottom": "20mm",
        "margin_left": "15mm",
        "margin_right": "15mm",
        "font_size": "11pt",
        "line_height": "1.6",
    }


def generate_print_css() -> str:
    """Generate CSS for print media with book formatting."""
    config = get_weasyprint_config()

    css = f"""
    @page {{
        size: {config['page_width']} {config['page_height']};
        margin-top: {config['margin_top']};
        margin-bottom: {config['margin_bottom']};
        margin-left: {config['margin_left']};
        margin-right: {config['margin_right']};

        @bottom-center {{
            content: counter(page);
            font-size: 10pt;
            color: #666;
        }}
    }}

    /* Typography and hyphenation */
    body {{
        font-family: 'Crimson Text', Georgia, serif;
        font-size: {config['font_size']};
        line-height: {config['line_height']};
        text-align: justify;
        hyphens: auto;
        hyphenate-language: "fr";
        hyphenate-limit-chars: 5 3 2;
    }}

    /* Prevent orphan titles */
    h1, h2, h3, h4, h5, h6 {{
        page-break-after: avoid;
        page-break-inside: avoid;
        orphans: 3;
        widows: 3;
    }}

    /* Prevent orphan paragraphs */
    p {{
        orphans: 3;
        widows: 3;
    }}

    /* Chapter breaks */
    .chapter {{
        page-break-before: always;
    }}

    /* Keep elements together */
    .keep-together {{
        page-break-inside: avoid;
    }}

    /* First page of chapter styling */
    .chapter-title {{
        margin-top: 60mm;
        margin-bottom: 30mm;
        text-align: center;
        page-break-after: avoid;
    }}

    /* Table of contents */
    .toc-entry {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5em;
        page-break-inside: avoid;
    }}

    .toc-title {{
        flex: 1;
        padding-right: 1em;
    }}

    .toc-dots {{
        flex: 0 0 auto;
        border-bottom: 1px dotted #666;
        margin: 0 0.5em;
        width: auto;
        min-width: 2em;
    }}

    .toc-page {{
        flex: 0 0 auto;
    }}

    /* Images */
    img {{
        max-width: 100%;
        height: auto;
        page-break-inside: avoid;
    }}

    /* Tables */
    table {{
        page-break-inside: avoid;
        border-collapse: collapse;
        width: 100%;
    }}

    /* Code blocks */
    pre {{
        page-break-inside: avoid;
        background-color: #f5f5f5;
        padding: 1em;
        border-radius: 3px;
        font-size: 9pt;
        overflow-wrap: break-word;
    }}

    /* Footnotes */
    .footnote {{
        font-size: 9pt;
        line-height: 1.4;
    }}

    /* Page numbers for references */
    .page-ref::after {{
        content: target-counter(attr(href), page);
    }}
    """

    return css


def is_weasyprint_available() -> bool:
    """Check if WeasyPrint is available for PDF generation."""
    return WEASYPRINT_AVAILABLE


def generate_test_pdf(html_content: str, output_path: str) -> bool:
    """Generate a test PDF from HTML content."""
    if not WEASYPRINT_AVAILABLE:
        logger.error("Cannot generate PDF: WeasyPrint is not installed")
        return False

    try:
        # Add basic HTML structure if not present
        if not html_content.startswith("<!DOCTYPE"):
            css = generate_print_css()
            html_content = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <style>
                {css}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

        # Generate PDF
        html = weasyprint.HTML(string=html_content)
        html.write_pdf(output_path)

        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

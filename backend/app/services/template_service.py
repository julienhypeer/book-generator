"""
Template service for CSS and HTML generation.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings


class TemplateService:
    """Service for managing templates and CSS generation."""
    
    def __init__(self):
        """Initialize template service."""
        self.template_dir = settings.storage_root / "templates"
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
    
    def generate_css(
        self,
        template_name: str = "professional",
        font_size: int = 11,
        line_height: float = 1.6,
        **kwargs
    ) -> str:
        """Generate CSS for a specific template."""
        # Base CSS for all templates
        base_css = """
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Page setup for book format */
        @page {
            size: 156mm 234mm;
            margin: 20mm 15mm;
            @bottom-center {
                content: counter(page);
                font-size: 10pt;
            }
        }
        
        /* Typography */
        body {
            font-family: 'BookSerif', Georgia, 'Times New Roman', serif;
            font-size: {font_size}pt;
            line-height: {line_height};
            text-align: justify;
            hyphens: auto;
            hyphenate-language: "fr";
            hyphenate-limit-chars: 5 3 2;
        }
        
        /* Headings */
        h1 {
            font-size: 24pt;
            margin: 2em 0 1em 0;
            page-break-after: avoid;
            page-break-inside: avoid;
            orphans: 3;
            widows: 3;
        }
        
        h2 {
            font-size: 18pt;
            margin: 1.5em 0 0.75em 0;
            page-break-after: avoid;
            page-break-inside: avoid;
            orphans: 3;
            widows: 3;
        }
        
        h3 {
            font-size: 14pt;
            margin: 1em 0 0.5em 0;
            page-break-after: avoid;
            page-break-inside: avoid;
            orphans: 3;
            widows: 3;
        }
        
        /* Paragraphs */
        p {
            margin: 0 0 1em 0;
            text-indent: 1.5em;
            orphans: 2;
            widows: 2;
        }
        
        p:first-of-type,
        h1 + p,
        h2 + p,
        h3 + p {
            text-indent: 0;
        }
        
        /* Lists */
        ul, ol {
            margin: 1em 0 1em 2em;
        }
        
        li {
            margin: 0.5em 0;
        }
        
        /* Code */
        code {
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            background: #f5f5f5;
            padding: 0.1em 0.3em;
        }
        
        pre {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            background: #f5f5f5;
            padding: 1em;
            margin: 1em 0;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        
        /* Blockquotes */
        blockquote {
            margin: 1em 2em;
            font-style: italic;
            border-left: 3px solid #ccc;
            padding-left: 1em;
        }
        
        /* Tables */
        table {
            width: 100%;
            margin: 1em 0;
            border-collapse: collapse;
            page-break-inside: avoid;
        }
        
        th, td {
            padding: 0.5em;
            border: 1px solid #ddd;
            text-align: left;
        }
        
        th {
            background: #f5f5f5;
            font-weight: bold;
        }
        
        /* Footnotes */
        .footnote {
            font-size: 0.85em;
            vertical-align: super;
        }
        
        .footnotes {
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #ccc;
            font-size: 0.9em;
        }
        
        /* Chapter breaks */
        .chapter-break {
            page-break-before: right;
        }
        
        /* TOC */
        .toc {
            page-break-after: always;
        }
        
        .toc-entry {
            display: flex;
            justify-content: space-between;
            margin: 0.5em 0;
        }
        
        .toc-title {
            flex: 1;
        }
        
        .toc-dots {
            flex: 0 0 auto;
            border-bottom: 1px dotted #333;
            margin: 0 0.5em;
        }
        
        .toc-page {
            flex: 0 0 auto;
        }
        """.format(font_size=font_size, line_height=line_height)
        
        # Template-specific styles
        template_css = ""
        
        if template_name == "professional":
            template_css = """
            /* Professional template additions */
            h1 {
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }
            
            h2 {
                border-bottom: 1px solid #333;
                padding-bottom: 0.25em;
            }
            """
        
        elif template_name == "modern":
            template_css = """
            /* Modern template additions */
            body {
                font-family: 'BookSans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            h1 {
                color: #2c3e50;
                font-weight: 300;
            }
            
            h2 {
                color: #34495e;
                font-weight: 400;
            }
            
            blockquote {
                border-left-color: #3498db;
            }
            """
        
        elif template_name == "classic":
            template_css = """
            /* Classic template additions */
            body {
                font-family: 'Garamond', 'Times New Roman', serif;
            }
            
            h1 {
                font-variant: small-caps;
                text-align: center;
            }
            
            h1:before, h1:after {
                content: "❦";
                display: inline-block;
                margin: 0 1em;
            }
            """
        
        return base_css + template_css
    
    def generate_html(
        self,
        content: str,
        title: str = "",
        author: str = "",
        template_name: str = "professional",
        **kwargs
    ) -> str:
        """Generate full HTML document with template."""
        css = self.generate_css(
            template_name=template_name,
            font_size=kwargs.get("font_size", 11),
            line_height=kwargs.get("line_height", 1.6)
        )
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="author" content="{author}">
    <style>
    {css}
    </style>
</head>
<body>
    {content}
</body>
</html>"""
        
        return html
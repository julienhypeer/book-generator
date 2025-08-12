"""Storage management for projects, templates and exports."""

import shutil
from pathlib import Path

from app.core.config import Settings, settings as default_settings


def get_project_path(project_id: str) -> Path:
    """Get the storage path for a specific project."""
    return default_settings.projects_dir / project_id


def init_storage(settings: Settings) -> None:
    """Initialize storage directory structure."""

    # Create main directories
    directories = [
        settings.projects_dir,
        settings.templates_dir,
        settings.exports_dir,
        settings.temp_dir,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # Clean temp directory
    clean_temp_directory(settings.temp_dir)

    # Copy default templates if not exist
    copy_default_templates(settings.templates_dir)


def clean_temp_directory(temp_dir: Path) -> None:
    """Clean temporary directory by removing all files."""
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def copy_default_templates(templates_dir: Path) -> None:
    """Copy default CSS templates if they don't exist."""

    default_templates = {
        "roman.css": generate_roman_template(),
        "technical.css": generate_technical_template(),
        "academic.css": generate_academic_template(),
    }

    for filename, content in default_templates.items():
        template_path = templates_dir / filename
        if not template_path.exists():
            template_path.write_text(content, encoding="utf-8")


def generate_roman_template() -> str:
    """Generate CSS template for roman/fiction books."""
    return """  # noqa: E501
    /* Roman/Fiction Book Template */
    @import url('../fonts/fonts.css');

    body {
        font-family: 'BookSerif', Georgia, serif;
        font-size: 11pt;
        line-height: 1.8;
        color: #2c2c2c;
    }

    h1 {
        font-size: 24pt;
        font-weight: normal;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 60mm 0 30mm 0;
        text-align: center;
    }

    h2 {
        font-size: 18pt;
        font-weight: normal;
        font-style: italic;
        margin: 20mm 0 10mm 0;
    }

    p {
        text-indent: 1.5em;
        margin: 0;
    }

    p.first {
        text-indent: 0;
    }

    .drop-cap {
        float: left;
        font-size: 48pt;
        line-height: 0.8;
        margin: 0.1em 0.1em 0 0;
    }

    blockquote {
        margin: 1em 2em;
        font-style: italic;
        color: #555;
    }
    """


def generate_technical_template() -> str:
    """Generate CSS template for technical documentation."""
    return """  # noqa: E501
    /* Technical Documentation Template */
    @import url('../fonts/fonts.css');

    body {
        font-family: 'BookSans', -apple-system, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.6;
        color: #333;
    }

    h1 {
        font-size: 20pt;
        font-weight: 700;
        border-bottom: 2px solid #2196F3;
        padding-bottom: 5mm;
        margin: 40mm 0 15mm 0;
    }

    h2 {
        font-size: 16pt;
        font-weight: 600;
        color: #2196F3;
        margin: 15mm 0 8mm 0;
    }

    h3 {
        font-size: 13pt;
        font-weight: 600;
        margin: 10mm 0 5mm 0;
    }

    code {
        font-family: 'BookMono', Consolas, Monaco, monospace;
        background-color: #f5f5f5;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-size: 9pt;
    }

    pre {
        background-color: #f5f5f5;
        border-left: 3px solid #2196F3;
        padding: 1em;
        font-size: 9pt;
        overflow-x: auto;
    }

    table {
        border: 1px solid #ddd;
        margin: 1em 0;
    }

    th {
        background-color: #f5f5f5;
        font-weight: 600;
        padding: 0.5em;
        text-align: left;
    }

    td {
        padding: 0.5em;
        border-top: 1px solid #ddd;
    }

    .note {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 1em;
        margin: 1em 0;
    }

    .warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1em;
        margin: 1em 0;
    }
    """


def generate_academic_template() -> str:
    """Generate CSS template for academic papers."""
    return """  # noqa: E501
    /* Academic Paper Template */
    @import url('../fonts/fonts.css');

    body {
        font-family: 'BookAcademic', 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 2;
        color: #000;
        text-align: justify;
    }

    h1 {
        font-size: 14pt;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        margin: 30mm 0 15mm 0;
    }

    h2 {
        font-size: 12pt;
        font-weight: bold;
        margin: 12mm 0 6mm 0;
    }

    h3 {
        font-size: 12pt;
        font-weight: normal;
        font-style: italic;
        margin: 8mm 0 4mm 0;
    }

    p {
        text-indent: 0.5in;
        margin: 0 0 12pt 0;
    }

    .abstract {
        margin: 0 1in;
        font-size: 11pt;
        text-align: justify;
    }

    .citation {
        margin-left: 0.5in;
        text-indent: -0.5in;
        margin-bottom: 12pt;
    }

    .footnote {
        font-size: 10pt;
        line-height: 1.5;
    }

    blockquote {
        margin: 0 0.5in;
        font-size: 11pt;
        line-height: 1.5;
    }
    """

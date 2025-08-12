"""
Template service for managing CSS styles and print rules.
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader, Template


@dataclass
class PageSettings:
    """Page settings for print layout."""

    format: str = "156mm 234mm"  # Standard book format
    margins: Dict[str, int] = field(
        default_factory=lambda: {"top": 20, "bottom": 20, "left": 15, "right": 15}
    )
    bleed: int = 3  # Bleed in mm for printing
    binding_offset: int = 0  # Extra margin for binding


@dataclass
class Typography:
    """Typography settings."""

    font_family: str = "Garamond, Georgia, serif"
    font_size: str = "11pt"
    line_height: float = 1.6
    text_align: str = "justify"
    hyphenation: bool = True
    language: str = "en"
    paragraph_indent: str = "0"
    drop_caps: bool = False
    quotes_style: str = "auto"  # auto, english, french
    spacing_rules: str = "auto"  # auto, english, french


@dataclass
class PrintRules:
    """Print-specific rules."""

    page_numbers: bool = True
    page_number_position: str = "bottom-center"
    page_number_format: str = "decimal"  # decimal, lower-roman, upper-roman
    running_headers: bool = False
    header_content: str = "chapter"  # chapter, title, section
    chapter_start: str = "auto"  # auto, right, left, any
    blank_pages: str = "auto"  # auto, remove, keep
    orphans: int = 3
    widows: int = 3


@dataclass
class TemplateConfig:
    """Complete template configuration."""

    template_name: str = "book"
    page_settings: Optional[PageSettings] = None
    typography: Optional[Typography] = None
    print_rules: Optional[PrintRules] = None
    color_scheme: str = "blackwhite"  # blackwhite, sepia, color
    custom_css: str = ""
    minify: bool = False
    use_cache: bool = True
    toc_settings: Dict[str, Any] = field(default_factory=dict)
    footnote_settings: Dict[str, Any] = field(default_factory=dict)
    image_settings: Dict[str, Any] = field(default_factory=dict)
    layout_settings: Dict[str, Any] = field(default_factory=dict)
    special_pages: Dict[str, Any] = field(default_factory=dict)
    responsive_print: bool = False


class TemplateService:
    """Service for managing templates and CSS generation."""

    # Standard page formats
    PAGE_FORMATS = {
        "A4": "210mm 297mm",
        "A5": "148mm 210mm",
        "Letter": "8.5in 11in",
        "Legal": "8.5in 14in",
        "book": "156mm 234mm",
        "pocket": "110mm 178mm",
        "trade": "5.5in 8.5in",
    }

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template service."""
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"

        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # CSS templates directory
        self.css_dir = self.templates_dir / "css"
        self.css_dir.mkdir(parents=True, exist_ok=True)

        # Initialize cache
        self._cache = {}

        # Available templates
        self.available_templates = ["book", "academic", "novel", "technical", "simple"]

        # Jinja environment for CSS templates
        self.jinja_env = Environment(
            loader=(
                FileSystemLoader(str(self.css_dir)) if self.css_dir.exists() else None
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_css(self, config: TemplateConfig) -> str:
        """Generate CSS based on configuration."""
        # Validate template
        if config.template_name not in self.available_templates:
            raise ValueError(f"Invalid template: {config.template_name}")

        # Check cache
        if config.use_cache:
            cache_key = self._get_cache_key(config)
            if cache_key in self._cache:
                return self._cache[cache_key]

        # Set defaults
        if config.page_settings is None:
            config.page_settings = PageSettings()
        if config.typography is None:
            config.typography = Typography()
        if config.print_rules is None:
            config.print_rules = PrintRules()

        # Generate base CSS
        css = self._generate_base_css(config)

        # Add template-specific CSS
        css += self._generate_template_css(config)

        # Add custom CSS
        if config.custom_css:
            css += f"\n\n/* Custom CSS */\n{config.custom_css}"

        # Minify if requested
        if config.minify:
            css = self.minify_css(css)

        # Cache result
        if config.use_cache:
            self._cache[cache_key] = css

        return css

    def _generate_base_css(self, config: TemplateConfig) -> str:
        """Generate base CSS rules."""
        ps = config.page_settings
        typo = config.typography
        pr = config.print_rules

        # Normalize page format
        page_format = ps.format
        if page_format in self.PAGE_FORMATS:
            page_format = self.PAGE_FORMATS[page_format]

        # Validate page format
        if not self._validate_page_format(page_format):
            raise ValueError(f"Invalid page format: {ps.format}")

        css = f"""
/* Base Print Styles */
@page {{
    size: {page_format};
    margin: {ps.margins['top']}mm {ps.margins['right']}mm {ps.margins['bottom']}mm {ps.margins['left']}mm;
    """

        # Add bleed if specified
        if ps.bleed > 0:
            css += f"\n    bleed: {ps.bleed}mm;"

        # Page numbering
        if pr.page_numbers:
            position = pr.page_number_position.replace("-", "_")
            css += f"""
    @{position.replace('_', '-')} {{
        content: counter(page{', ' + pr.page_number_format if pr.page_number_format != 'decimal' else ''});
    }}"""

        css += "\n}\n"

        # Running headers
        if pr.running_headers:
            css += """
@page :left {
    @top-left {
        content: string(chapter-title);
    }
}

@page :right {
    @top-right {
        content: string(section-title);
    }
}
"""

        # Typography
        color = "black"
        if config.color_scheme == "sepia":
            color = "#5c4033"
        elif config.color_scheme != "blackwhite":
            color = "#333"

        css += f"""
/* Typography */
body {{
    font-family: {typo.font_family};
    font-size: {typo.font_size};
    line-height: {typo.line_height};
    text-align: {typo.text_align};
    color: {color};
}}

p {{
    margin: 0 0 1em 0;
    {'text-indent: ' + typo.paragraph_indent + ';' if typo.paragraph_indent != '0' else ''}
    {'hyphens: auto;' if typo.hyphenation else 'hyphens: none;'}
    {f'hyphenate-language: "{typo.language}";' if typo.hyphenation else ''}
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    page-break-after: avoid;
    page-break-inside: avoid;
    orphans: {pr.orphans};
    widows: {pr.widows};
}}

h1 {{
    font-size: 2em;
    margin: 2em 0 1em 0;
    {f'page-break-before: {pr.chapter_start};' if pr.chapter_start != 'auto' else ''}
}}

h2 {{
    font-size: 1.5em;
    margin: 1.5em 0 0.75em 0;
}}

h3 {{
    font-size: 1.2em;
    margin: 1.2em 0 0.6em 0;
}}

/* Orphans and Widows */
p, li, blockquote {{
    orphans: {pr.orphans};
    widows: {pr.widows};
}}
"""

        # Drop caps
        if typo.drop_caps:
            css += """
/* Drop Caps */
.chapter > p:first-of-type:first-letter,
p.first:first-letter {
    font-size: 3em;
    line-height: 1;
    float: left;
    margin: 0 0.1em 0 0;
}
"""

        # Language-specific rules
        if typo.language == "fr" or typo.spacing_rules == "french":
            css += """
/* French Typography */
:lang(fr) {
    quotes: "«" "»" "‹" "›";
}
"""

        # Quotes style
        if typo.quotes_style == "french":
            css += """
body {
    quotes: "«" "»" "‹" "›";
}
"""
        elif typo.quotes_style == "english":
            css += (
                """
body {
    quotes: """
                """ "'" "'";
}
"""
            )

        return css

    def _generate_template_css(self, config: TemplateConfig) -> str:
        """Generate template-specific CSS."""
        css = f"\n/* Template: {config.template_name} */\n"

        if config.template_name == "book":
            css += self._generate_book_css(config)
        elif config.template_name == "academic":
            css += self._generate_academic_css(config)
        elif config.template_name == "novel":
            css += self._generate_novel_css(config)
        elif config.template_name == "technical":
            css += self._generate_technical_css(config)
        else:
            css += self._generate_simple_css(config)

        # TOC styling
        if config.toc_settings:
            css += self._generate_toc_css(config.toc_settings)

        # Footnotes
        if config.footnote_settings:
            css += self._generate_footnote_css(config.footnote_settings)

        # Images
        if config.image_settings:
            css += self._generate_image_css(config.image_settings)

        # Multi-column layout
        if config.layout_settings.get("columns"):
            css += self._generate_column_css(config.layout_settings)

        # Special pages
        if config.special_pages:
            css += self._generate_special_pages_css(config.special_pages)

        # Responsive print
        if config.responsive_print:
            css += self._generate_responsive_print_css()

        return css

    def _generate_book_css(self, config: TemplateConfig) -> str:
        """Generate book-specific CSS."""
        return """
/* Book Template */
.chapter {
    page-break-before: right;
}

.part {
    page-break-before: right;
    text-align: center;
    margin: 30% 0;
}

.frontmatter {
    page: frontmatter;
}

.mainmatter {
    page: mainmatter;
    counter-reset: page 1;
}

.backmatter {
    page: backmatter;
}

/* Chapter numbers */
h1::before {
    content: "Chapter " counter(chapter) ": ";
    counter-increment: chapter;
}
"""

    def _generate_academic_css(self, config: TemplateConfig) -> str:
        """Generate academic-specific CSS."""
        return """
/* Academic Template */
.abstract {
    font-size: 0.9em;
    margin: 2em 4em;
    font-style: italic;
}

.citation {
    margin-left: 2em;
    font-size: 0.95em;
}

.references {
    font-size: 0.9em;
}

.references li {
    margin-bottom: 0.5em;
}

/* Sections numbering */
h2::before {
    content: counter(chapter) "." counter(section) " ";
    counter-increment: section;
}

h3::before {
    content: counter(chapter) "." counter(section) "." counter(subsection) " ";
    counter-increment: subsection;
}
"""

    def _generate_novel_css(self, config: TemplateConfig) -> str:
        """Generate novel-specific CSS."""
        css = """
/* Novel Template */
.chapter {
    page-break-before: always;
}

.scene-break {
    text-align: center;
    margin: 2em 0;
}

.scene-break::before {
    content: "* * *";
}

p {
    text-indent: 1.5em;
}

p.first,
.chapter > p:first-of-type {
    text-indent: 0;
}
"""
        if config.typography and config.typography.drop_caps:
            css += """
/* Drop caps for first paragraph */
.chapter > p:first-of-type::first-letter {
    font-size: 4em;
    line-height: 0.8;
    float: left;
    margin: 0 0.05em -0.1em 0;
    font-weight: bold;
}
"""
        return css

    def _generate_technical_css(self, config: TemplateConfig) -> str:
        """Generate technical documentation CSS."""
        return """
/* Technical Template */
code {
    font-family: 'Courier New', monospace;
    background: #f5f5f5;
    padding: 0.2em 0.4em;
}

pre {
    background: #f5f5f5;
    padding: 1em;
    overflow-x: auto;
    page-break-inside: avoid;
}

.warning,
.note,
.tip {
    padding: 1em;
    margin: 1em 0;
    page-break-inside: avoid;
}

.warning {
    border-left: 4px solid #ff9800;
    background: #fff3e0;
}

.note {
    border-left: 4px solid #2196f3;
    background: #e3f2fd;
}
"""

    def _generate_simple_css(self, config: TemplateConfig) -> str:
        """Generate simple/minimal CSS."""
        return """
/* Simple Template */
h1 {
    page-break-before: always;
}

img {
    max-width: 100%;
    height: auto;
}
"""

    def _generate_toc_css(self, settings: Dict[str, Any]) -> str:
        """Generate TOC CSS."""
        css = """
/* Table of Contents */
.toc {
    page-break-after: always;
}

.toc li {
    list-style: none;
    margin: 0.5em 0;
}
"""
        if settings.get("show_page_numbers"):
            css += """
.toc a::after {
    content: leader(dotted) " " target-counter(attr(href), page);
}
"""
        if settings.get("indent_levels"):
            css += """
.toc li.level-2 {
    margin-left: 2em;
}
.toc li.level-3 {
    margin-left: 4em;
}
"""
        return css

    def _generate_footnote_css(self, settings: Dict[str, Any]) -> str:
        """Generate footnote CSS."""
        css = """
/* Footnotes */
.footnote {
    font-size: 0.9em;
    margin-top: 1em;
}
"""
        if settings.get("separator"):
            css += """
.footnote {
    border-top: 1px solid #ccc;
    padding-top: 0.5em;
}
"""
        return css

    def _generate_image_css(self, settings: Dict[str, Any]) -> str:
        """Generate image CSS."""
        css = """
/* Images */
img {
    max-width: 100%;
    height: auto;
}

figure {
    margin: 1em 0;
    text-align: center;
    page-break-inside: avoid;
}

figcaption {
    font-size: 0.9em;
    font-style: italic;
    margin-top: 0.5em;
}
"""
        return css

    def _generate_column_css(self, settings: Dict[str, Any]) -> str:
        """Generate multi-column CSS."""
        return f"""
/* Multi-column Layout */
.columns {{
    column-count: {settings.get('columns', 2)};
    column-gap: {settings.get('column_gap', '20px')};
    {'column-rule: ' + settings['column_rule'] + ';' if settings.get('column_rule') else ''}
}}
"""

    def _generate_special_pages_css(self, pages: Dict[str, Any]) -> str:
        """Generate special pages CSS."""
        css = "\n/* Special Pages */\n"

        for page_class, styles in pages.items():
            css_class = page_class.replace("_", "-")
            css += f".{css_class} {{\n"
            for prop, value in styles.items():
                css_prop = prop.replace("_", "-")
                css += f"    {css_prop}: {value};\n"
            css += "}\n"

        return css

    def _generate_responsive_print_css(self) -> str:
        """Generate responsive print media queries."""
        return """
/* Responsive Print */
@media print and (width: 210mm) {
    /* A4 specific rules */
    body { font-size: 11pt; }
}

@media print and (width: 156mm) {
    /* Book format specific rules */
    body { font-size: 10pt; }
}
"""

    def minify_css(self, css: str) -> str:
        """Minify CSS for production."""
        # Remove comments
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
        # Remove extra whitespace
        css = re.sub(r"\s+", " ", css)
        # Remove whitespace around special characters
        css = re.sub(r"\s*([{}:;,])\s*", r"\1", css)
        # Remove trailing semicolon before }
        css = re.sub(r";\}", "}", css)

        return css.strip()

    def clear_cache(self):
        """Clear CSS cache."""
        self._cache.clear()

    def export_css(self, css: str, output_file: Path):
        """Export CSS to file."""
        output_file.write_text(css, encoding="utf-8")

    def generate_preview(self, config: TemplateConfig, sample_content: str = "") -> str:
        """Generate HTML preview with CSS."""
        css = self.generate_css(config)

        if not sample_content:
            sample_content = """
            <h1>Sample Chapter</h1>
            <p>This is a sample paragraph to preview the template styling.</p>
            <h2>Section Title</h2>
            <p>Another paragraph with some <strong>bold</strong> and <em>italic</em> text.</p>
            """

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Template Preview</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="content">
{sample_content}
    </div>
</body>
</html>"""

        return html

    def _get_cache_key(self, config: TemplateConfig) -> str:
        """Generate cache key for configuration."""
        config_str = str(sorted(config.__dict__.items()))
        return hashlib.md5(config_str.encode()).hexdigest()

    def _validate_page_format(self, format_str: str) -> bool:
        """Validate page format string."""
        # Check for valid format patterns
        patterns = [
            r"^\d+mm \d+mm$",  # mm format
            r"^\d+\.?\d*in \d+\.?\d*in$",  # inch format
            r"^[A-Z]\d$",  # A4, A5, etc.
        ]

        for pattern in patterns:
            if re.match(pattern, format_str):
                return True

        return False

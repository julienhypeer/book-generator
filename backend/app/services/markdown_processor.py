"""
Enhanced Markdown processor service with full extensions support.
Includes python-markdown[extra] and pymdown-extensions for professional book generation.
"""

import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

import markdown
from markdown.extensions import Extension
from markdown.extensions.toc import TocExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.meta import MetaExtension
from markdown.extensions.attr_list import AttrListExtension
from markdown.extensions.def_list import DefListExtension
from markdown.extensions.abbr import AbbrExtension
from markdown.extensions.smarty import SmartyExtension
from markdown.extensions.admonition import AdmonitionExtension
from markdown.extensions.nl2br import Nl2BrExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.extra import ExtraExtension
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from markupsafe import Markup
import bleach

# Try to import pymdown-extensions for advanced features
try:
    import pymdownx
    PYMDOWN_AVAILABLE = True
except ImportError:
    PYMDOWN_AVAILABLE = False


@dataclass
class MarkdownConfig:
    """Enhanced configuration for markdown processing with full extension support."""

    # Core extensions (markdown[extra])
    enable_extra: bool = True  # Includes tables, footnotes, abbreviations, etc.
    enable_toc: bool = True
    enable_tables: bool = True
    enable_footnotes: bool = True
    enable_codehilite: bool = True
    enable_meta: bool = True

    # Additional standard extensions
    enable_attr_list: bool = True
    enable_def_list: bool = True
    enable_abbr: bool = True
    enable_smarty: bool = True  # For French typography (guillemets)
    enable_heading_ids: bool = True
    enable_admonition: bool = True  # For notes, warnings, etc.
    enable_nl2br: bool = False  # New line to break
    enable_sane_lists: bool = True
    enable_fenced_code: bool = True

    # PyMdown Extensions (if available)
    enable_pymdown: bool = True
    enable_math: bool = True  # Via pymdownx.arithmatex
    enable_superfences: bool = True  # Advanced code blocks
    enable_critic: bool = True  # Track changes
    enable_caret: bool = True  # Superscript
    enable_tilde: bool = True  # Subscript and strikethrough
    enable_mark: bool = True  # Highlight
    enable_smartsymbols: bool = True  # Smart symbols
    enable_tasklist: bool = True  # Task lists
    enable_emoji: bool = False  # Emoji support
    enable_magiclink: bool = True  # Auto-link URLs
    
    # Typography and language
    language: str = "fr"  # Default to French for guillemets
    quotes_style: str = "french"  # french, english, auto
    
    # Cross-references and figures
    enable_figures: bool = True
    enable_cross_refs: bool = True

    # Custom extensions
    custom_extensions: List[str] = field(default_factory=list)

    # Processing options
    sanitize_html: bool = True
    use_cache: bool = True

    # Template options
    template_dir: str = "templates"

    def get_extensions(self) -> List:
        """Get comprehensive list of markdown extensions based on config."""
        extensions = []

        # Use markdown[extra] if enabled (recommended)
        if self.enable_extra:
            extensions.append('extra')
        else:
            # Add individual extensions if extra is disabled
            if self.enable_tables:
                extensions.append(TableExtension())
            if self.enable_footnotes:
                extensions.append(FootnoteExtension())
            if self.enable_abbr:
                extensions.append(AbbrExtension())
            if self.enable_attr_list:
                extensions.append(AttrListExtension())
            if self.enable_def_list:
                extensions.append(DefListExtension())

        # Table of Contents with French-friendly slugification
        if self.enable_toc:
            extensions.append(
                TocExtension(
                    baselevel=1,
                    permalink=True,
                    permalink_class="headerlink",
                    slugify=lambda value, separator: re.sub(r"[^\w\s-]", "", value)
                    .strip()
                    .lower()
                    .replace(" ", separator),
                )
            )

        # Code highlighting
        if self.enable_codehilite:
            extensions.append(
                CodeHiliteExtension(
                    css_class="highlight", 
                    linenums=False, 
                    guess_lang=True
                )
            )
        
        # Fenced code blocks (```)
        if self.enable_fenced_code:
            extensions.append(FencedCodeExtension())

        # Metadata support
        if self.enable_meta:
            extensions.append(MetaExtension())

        # Smart typography for French (guillemets, etc.)
        if self.enable_smarty:
            smarty_config = {
                'smart_quotes': True,
                'smart_dashes': True,
                'smart_ellipses': True,
            }
            # French typography settings
            if self.language == "fr" or self.quotes_style == "french":
                smarty_config['substitutions'] = {
                    'left-single-quote': "'",  # Keep simple quotes as is
                    'right-single-quote': "'",  # Keep simple quotes as is
                    'left-double-quote': '«\u00A0',  # With non-breaking space
                    'right-double-quote': '\u00A0»',
                    'left-angle-quote': '«\u00A0',  # Explicitly handle angle quotes
                    'right-angle-quote': '\u00A0»',
                }
            extensions.append(SmartyExtension(**smarty_config))

        # Admonitions (notes, warnings, etc.)
        if self.enable_admonition:
            extensions.append(AdmonitionExtension())

        # New line to break
        if self.enable_nl2br:
            extensions.append(Nl2BrExtension())

        # Sane lists
        if self.enable_sane_lists:
            extensions.append(SaneListExtension())

        # PyMdown Extensions (if available and enabled)
        if PYMDOWN_AVAILABLE and self.enable_pymdown:
            # Math support
            if self.enable_math:
                extensions.append('pymdownx.arithmatex')
                
            # Advanced code blocks
            if self.enable_superfences:
                extensions.append('pymdownx.superfences')
                
            # Track changes
            if self.enable_critic:
                extensions.append('pymdownx.critic')
                
            # Superscript/Subscript
            if self.enable_caret:
                extensions.append('pymdownx.caret')
            if self.enable_tilde:
                extensions.append('pymdownx.tilde')
                
            # Highlighting
            if self.enable_mark:
                extensions.append('pymdownx.mark')
                
            # Smart symbols
            if self.enable_smartsymbols:
                extensions.append('pymdownx.smartsymbols')
                
            # Task lists
            if self.enable_tasklist:
                extensions.append('pymdownx.tasklist')
                
            # Emoji
            if self.enable_emoji:
                extensions.append('pymdownx.emoji')
                
            # Auto-link URLs
            if self.enable_magiclink:
                extensions.append('pymdownx.magiclink')

        # Add custom extensions
        for ext in self.custom_extensions:
            try:
                extensions.append(ext)
            except ImportError:
                print(f"Warning: Could not load extension {ext}")

        return extensions


class MarkdownProcessor:
    """Service for processing markdown with various extensions."""

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize the markdown processor."""
        self._cache = {}
        self._md_instances = {}

        # Setup Jinja2 environment
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        self.template_dir = template_dir
        self.jinja_env = Environment(
            loader=(
                FileSystemLoader(str(template_dir)) if template_dir.exists() else None
            ),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Configure bleach for HTML sanitization
        self.allowed_tags = bleach.ALLOWED_TAGS | {
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "table",
            "thead",
            "tbody",
            "tr",
            "th",
            "td",
            "figure",
            "figcaption",
            "img",
            "pre",
            "code",
            "blockquote",
            "dl",
            "dt",
            "dd",
            "abbr",
            "sup",
            "sub",
            "hr",
            "br",
            "div",
            "span",
            "p",
        }

        self.allowed_attributes = {
            "*": ["class", "id"],
            "a": ["href", "title", "rel"],
            "img": ["src", "alt", "title", "width", "height"],
            "abbr": ["title"],
            "code": ["class"],
            "th": ["align", "style"],
            "td": ["align", "style"],
        }

    def _get_cache_key(self, content: str, config: MarkdownConfig) -> str:
        """Generate cache key for markdown content."""
        config_str = str(sorted(config.__dict__.items()))
        combined = f"{content}:{config_str}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_markdown_instance(self, config: MarkdownConfig) -> markdown.Markdown:
        """Get or create a markdown instance for the config."""
        # Create a hashable key from config
        config_key = str(sorted(config.__dict__.items()))

        if config_key not in self._md_instances:
            self._md_instances[config_key] = markdown.Markdown(
                extensions=config.get_extensions(), output_format="html5"
            )

        return self._md_instances[config_key]

    def convert(
        self,
        content: str,
        config: Optional[MarkdownConfig] = None,
        use_cache: Optional[bool] = None,
    ) -> str:
        """Convert markdown to HTML."""
        if content is None:
            raise ValueError("Content cannot be None")

        if not isinstance(content, str):
            raise TypeError(f"Content must be string, got {type(content)}")

        if not content:
            return ""

        if config is None:
            config = MarkdownConfig()

        use_cache = config.use_cache if use_cache is None else use_cache

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(content, config)
            if cache_key in self._cache:
                return self._cache[cache_key]

        # Get markdown instance
        md = self._get_markdown_instance(config)

        # Convert markdown to HTML
        html = md.convert(content)

        # Reset the markdown instance for next use
        md.reset()

        # Apply French typography if needed
        if config.language == "fr":
            html = self._apply_french_typography(html)

        # Handle math if enabled
        if config.enable_math:
            html = self._process_math(html)

        # Handle figures if enabled
        if config.enable_figures:
            html = self._process_figures(html)

        # Handle cross-references if enabled
        if config.enable_cross_refs:
            html = self._process_cross_refs(html)

        # Sanitize HTML if needed
        if config.sanitize_html:
            html = bleach.clean(
                html,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True,
            )

        # Cache the result
        if use_cache:
            self._cache[cache_key] = html

        return html

    def convert_with_metadata(
        self, content: str, config: Optional[MarkdownConfig] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Convert markdown and extract metadata."""
        if config is None:
            config = MarkdownConfig(enable_meta=True)
        else:
            config.enable_meta = True

        md = self._get_markdown_instance(config)
        html = md.convert(content)

        # Extract metadata
        metadata = {}
        if hasattr(md, "Meta"):
            for key, value in md.Meta.items():
                if len(value) == 1:
                    # Single value
                    metadata[key] = value[0]
                else:
                    # Multiple values
                    metadata[key] = value

        md.reset()

        # Sanitize if needed
        if config.sanitize_html:
            html = bleach.clean(
                html,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True,
            )

        return html, metadata

    def batch_convert(
        self, chapters: List[Dict[str, Any]], config: Optional[MarkdownConfig] = None
    ) -> List[Dict[str, Any]]:
        """Batch convert multiple chapters."""
        if config is None:
            config = MarkdownConfig()

        results = []
        for chapter in chapters:
            html = self.convert(chapter["content"], config)
            results.append(
                {"id": chapter["id"], "html": html, "content": chapter["content"]}
            )

        return results

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render HTML template with context."""
        # Add default margins if not provided
        if "margins" not in context:
            context["margins"] = {"top": 20, "bottom": 20, "left": 15, "right": 15}

        if self.jinja_env.loader is None:
            # Create a simple template if no template directory
            template_str = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    {% if toc %}
    <nav class="toc">
        {{ toc_content | safe }}
    </nav>
    {% endif %}
    
    <main>
        <h1>{{ chapter_title }}</h1>
        {{ content | safe }}
    </main>
    
    {% if page_numbers %}
    <footer class="page-number"></footer>
    {% endif %}
</body>
</html>"""
            template = Template(template_str)
        else:
            template = self.jinja_env.get_template(template_name)

        # Ensure content is marked as safe HTML
        if "content" in context:
            context["content"] = Markup(context["content"])

        return template.render(**context)

    def _apply_french_typography(self, html: str) -> str:
        """Apply French typography rules."""
        # Add non-breaking spaces before punctuation
        html = re.sub(r"\s+([!?:;])", r"&nbsp;\1", html)

        # French quotes
        html = re.sub(r"&quot;([^&]+)&quot;", r"«&nbsp;\1&nbsp;»", html)

        return html

    def _process_math(self, html: str) -> str:
        """Process math expressions for MathJax/KaTeX."""
        # Inline math: $...$
        html = re.sub(r"\$([^\$]+)\$", r'<span class="math inline">\1</span>', html)

        # Display math: $$...$$
        html = re.sub(r"\$\$([^\$]+)\$\$", r'<div class="math display">\1</div>', html)

        return html

    def _process_figures(self, html: str) -> str:
        """Process images with captions into figure elements."""
        # Pattern for images with title attribute
        pattern = r'<img ([^>]*?)alt="([^"]*?)"([^>]*?)title="([^"]*?)"([^>]*?)>'

        def replace_with_figure(match):
            attrs1, alt, attrs2, title, attrs3 = match.groups()
            img_tag = f'<img {attrs1}alt="{alt}"{attrs2}{attrs3}>'
            return f"<figure>{img_tag}<figcaption>{title}</figcaption></figure>"

        html = re.sub(pattern, replace_with_figure, html)

        return html

    def _process_cross_refs(self, html: str) -> str:
        """Process cross-references between sections."""
        # This is a simplified implementation
        # In production, would need more sophisticated reference tracking

        # Pattern for references like [](#section-id)
        pattern = r'<a href="#([^"]+)">([^<]*)</a>'

        def enhance_ref(match):
            ref_id, text = match.groups()
            if not text:
                # Try to find the referenced heading
                text = f"Section {ref_id}"
            return f'<a href="#{ref_id}" class="cross-ref">{text}</a>'

        html = re.sub(pattern, enhance_ref, html)

        return html

    def clear_cache(self):
        """Clear the conversion cache."""
        self._cache.clear()
        self._md_instances.clear()

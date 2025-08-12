"""
Tests for template service with CSS styles and print rules.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from app.services.template_service import (
    TemplateService,
    TemplateConfig,
    PageSettings,
    Typography,
    PrintRules,
)


class TestTemplateService:
    """Test suite for template service."""

    @pytest.fixture
    def service(self):
        """Create a template service instance."""
        return TemplateService()

    @pytest.fixture
    def page_settings(self):
        """Create default page settings."""
        return PageSettings(
            format="156mm 234mm",  # Standard book format
            margins={"top": 20, "bottom": 20, "left": 15, "right": 15},
            bleed=3,  # 3mm bleed for printing
        )

    @pytest.fixture
    def typography(self):
        """Create typography settings."""
        return Typography(
            font_family="Garamond, Georgia, serif",
            font_size="11pt",
            line_height=1.6,
            text_align="justify",
            hyphenation=True,
            language="fr",
        )

    @pytest.fixture
    def print_rules(self):
        """Create print rules."""
        return PrintRules(
            page_numbers=True,
            page_number_position="bottom-center",
            running_headers=True,
            chapter_start="right",  # Chapters start on right page
            blank_pages="auto",  # Auto insert for right-page starts
            orphans=3,
            widows=3,
        )

    def test_template_initialization(self, service):
        """Test template service initialization."""
        assert service is not None
        assert service.templates_dir.exists()
        assert len(service.available_templates) >= 3  # book, academic, novel

    def test_book_template_generation(self, service, page_settings, typography):
        """Test book template CSS generation."""
        config = TemplateConfig(
            template_name="book",
            page_settings=page_settings,
            typography=typography,
            custom_css="",
        )

        css = service.generate_css(config)

        # Check page rules
        assert "@page" in css
        assert "156mm 234mm" in css
        assert "margin: 20mm 15mm" in css

        # Check typography
        assert "font-family: Garamond" in css
        assert "font-size: 11pt" in css
        assert "line-height: 1.6" in css
        assert "text-align: justify" in css
        assert "hyphens: auto" in css

    def test_academic_template_generation(self, service):
        """Test academic template with specific requirements."""
        config = TemplateConfig(
            template_name="academic",
            page_settings=PageSettings(
                format="A4",
                margins={"top": 25, "bottom": 25, "left": 30, "right": 20},
            ),
            typography=Typography(
                font_family="Times New Roman, serif",
                font_size="12pt",
                line_height=2.0,  # Double spacing
                text_align="left",  # Left aligned for academic
            ),
        )

        css = service.generate_css(config)

        assert "@page" in css
        assert "A4" in css or "210mm 297mm" in css
        assert "Times New Roman" in css
        assert "line-height: 2" in css
        assert "text-align: left" in css

    def test_novel_template_generation(self, service):
        """Test novel template with specific styling."""
        config = TemplateConfig(
            template_name="novel",
            page_settings=PageSettings(
                format="5.5in 8.5in",  # US Trade Paperback
                margins={"top": 18, "bottom": 18, "left": 17, "right": 17},
            ),
            typography=Typography(
                font_family="Baskerville, Georgia, serif",
                font_size="10.5pt",
                line_height=1.5,
                paragraph_indent="1.5em",
                drop_caps=True,
            ),
        )

        css = service.generate_css(config)

        assert "5.5in 8.5in" in css
        assert "Baskerville" in css
        assert "text-indent: 1.5em" in css
        # Drop caps styling
        assert "first-letter" in css or "initial-letter" in css

    def test_page_break_rules(self, service, print_rules):
        """Test page break rules for avoiding orphans and widows."""
        config = TemplateConfig(
            template_name="book",
            print_rules=print_rules,
        )

        css = service.generate_css(config)

        # Check orphans and widows
        assert "orphans: 3" in css
        assert "widows: 3" in css

        # Check heading protection
        assert "page-break-after: avoid" in css
        assert "page-break-inside: avoid" in css

        # Check chapter start rules
        assert "page-break-before: right" in css

    def test_page_numbering_rules(self, service, print_rules):
        """Test page numbering configuration."""
        # Bottom center numbering
        config = TemplateConfig(
            template_name="book",
            print_rules=PrintRules(
                page_numbers=True,
                page_number_position="bottom-center",
                page_number_format="decimal",  # 1, 2, 3
            ),
        )

        css = service.generate_css(config)
        assert "@bottom-center" in css
        assert "counter(page)" in css

        # Roman numerals for front matter
        config.print_rules.page_number_format = "lower-roman"
        css = service.generate_css(config)
        assert "lower-roman" in css or "content: counter(page, lower-roman)" in css

    def test_running_headers(self, service):
        """Test running headers configuration."""
        config = TemplateConfig(
            template_name="book",
            print_rules=PrintRules(
                running_headers=True,
                header_content="chapter",  # Show chapter title
            ),
        )

        css = service.generate_css(config)

        assert "@top-left" in css or "@top-right" in css
        assert "string(chapter" in css or "content:" in css

    def test_toc_page_references(self, service):
        """Test TOC with page references."""
        config = TemplateConfig(
            template_name="book",
            toc_settings={
                "show_page_numbers": True,
                "dot_leader": True,
                "indent_levels": True,
            },
        )

        css = service.generate_css(config)

        # Check for TOC styling
        assert ".toc" in css
        # Dot leaders between title and page number
        assert "leader(dotted)" in css or "content: '.'" in css
        # Page references
        assert "target-counter" in css or "page-ref" in css

    def test_footnotes_styling(self, service):
        """Test footnotes styling for print."""
        config = TemplateConfig(
            template_name="academic",
            footnote_settings={
                "position": "bottom",  # Bottom of page
                "separator": True,
                "numbering": "decimal",
            },
        )

        css = service.generate_css(config)

        assert ".footnote" in css
        assert "border-top" in css  # Separator line
        assert "font-size: 0.9em" in css or "font-size: smaller" in css

    def test_image_handling(self, service):
        """Test image handling for print."""
        config = TemplateConfig(
            template_name="book",
            image_settings={
                "max_width": "100%",
                "center": True,
                "page_break": "avoid",  # Keep with caption
            },
        )

        css = service.generate_css(config)

        assert "img" in css
        assert "max-width: 100%" in css
        assert "page-break-inside: avoid" in css
        # Figure and caption together
        assert "figure" in css

    def test_custom_css_integration(self, service):
        """Test custom CSS integration."""
        custom_css = """
        .custom-class {
            color: #333;
            font-weight: bold;
        }
        
        @page chapter {
            @top-right {
                content: string(chapter-title);
            }
        }
        """

        config = TemplateConfig(
            template_name="book",
            custom_css=custom_css,
        )

        css = service.generate_css(config)

        assert ".custom-class" in css
        assert "color: #333" in css
        assert "@page chapter" in css

    def test_language_specific_typography(self, service):
        """Test language-specific typography rules."""
        # French typography
        config_fr = TemplateConfig(
            template_name="book",
            typography=Typography(
                language="fr",
                quotes_style="french",  # « »
                spacing_rules="french",  # Space before : ; ! ?
            ),
        )

        css_fr = service.generate_css(config_fr)
        assert 'quotes: "«" "»"' in css_fr or "guillemets" in css_fr
        assert "fr" in css_fr

        # English typography
        config_en = TemplateConfig(
            template_name="book",
            typography=Typography(
                language="en",
                quotes_style="english",  # "" ''
            ),
        )

        css_en = service.generate_css(config_en)
        assert "en" in css_en

    def test_color_themes(self, service):
        """Test different color themes for print."""
        # Black and white
        config_bw = TemplateConfig(
            template_name="book",
            color_scheme="blackwhite",
        )

        css_bw = service.generate_css(config_bw)
        assert "color: black" in css_bw or "color: #000" in css_bw
        assert "grayscale" not in css_bw or "filter: grayscale" in css_bw

        # Sepia for novels
        config_sepia = TemplateConfig(
            template_name="novel",
            color_scheme="sepia",
        )

        css_sepia = service.generate_css(config_sepia)
        # Sepia tones for comfortable reading
        assert "#5c4033" in css_sepia or "sepia" in css_sepia

    def test_multi_column_layout(self, service):
        """Test multi-column layout for certain sections."""
        config = TemplateConfig(
            template_name="academic",
            layout_settings={
                "columns": 2,
                "column_gap": "20px",
                "column_rule": "1px solid #ccc",
            },
        )

        css = service.generate_css(config)

        assert "column-count: 2" in css
        assert "column-gap: 20px" in css
        assert "column-rule" in css

    def test_special_pages(self, service):
        """Test special page types (title, copyright, etc.)."""
        config = TemplateConfig(
            template_name="book",
            special_pages={
                "title_page": {"text_align": "center", "margin_top": "30%"},
                "copyright_page": {"font_size": "0.9em", "page_break_after": "always"},
                "dedication": {"font_style": "italic", "text_align": "center"},
            },
        )

        css = service.generate_css(config)

        assert ".title-page" in css
        assert ".copyright-page" in css
        assert ".dedication" in css
        assert "page-break-after: always" in css

    def test_css_validation(self, service):
        """Test CSS validation for common errors."""
        # Invalid config should raise error
        with pytest.raises(ValueError):
            config = TemplateConfig(
                template_name="invalid_template",
            )
            service.generate_css(config)

        # Invalid page size
        with pytest.raises(ValueError):
            config = TemplateConfig(
                template_name="book",
                page_settings=PageSettings(format="invalid"),
            )
            service.generate_css(config)

    def test_css_minification(self, service):
        """Test CSS minification for production."""
        # First generate non-minified CSS
        config_normal = TemplateConfig(
            template_name="book",
            minify=False,
        )
        css_normal = service.generate_css(config_normal)

        # Then generate minified CSS
        config_minified = TemplateConfig(
            template_name="book",
            minify=True,
        )
        css_minified = service.generate_css(config_minified)

        # Minified should be smaller
        assert len(css_minified) < len(css_normal)
        # No unnecessary whitespace
        assert "  " not in css_minified
        assert "\n\n" not in css_minified

    def test_template_caching(self, service):
        """Test template caching for performance."""
        config = TemplateConfig(
            template_name="book",
            use_cache=True,
        )

        # First generation
        css1 = service.generate_css(config)

        # Second generation (should use cache)
        css2 = service.generate_css(config)

        assert css1 == css2

        # Clear cache
        service.clear_cache()

        # After cache clear, should regenerate
        css3 = service.generate_css(config)
        assert css3 == css1  # Content same, but regenerated

    def test_responsive_print_media(self, service):
        """Test responsive print media queries."""
        config = TemplateConfig(
            template_name="book",
            responsive_print=True,
        )

        css = service.generate_css(config)

        # Different rules for different paper sizes
        assert "@media print and (width: 210mm)" in css  # A4
        assert "@media print and (width: 156mm)" in css  # Book

    def test_export_css_file(self, service, tmp_path):
        """Test exporting CSS to file."""
        config = TemplateConfig(template_name="book")

        css = service.generate_css(config)
        output_file = tmp_path / "book.css"

        service.export_css(css, output_file)

        assert output_file.exists()
        assert output_file.read_text() == css

    def test_template_preview(self, service):
        """Test template preview generation."""
        config = TemplateConfig(template_name="book")

        preview_html = service.generate_preview(
            config,
            sample_content="""
            <h1>Chapter 1: Introduction</h1>
            <p>This is a sample paragraph.</p>
            <h2>Section 1.1</h2>
            <p>Another paragraph here.</p>
            """,
        )

        assert "<html" in preview_html
        assert "<style>" in preview_html
        assert "Chapter 1" in preview_html

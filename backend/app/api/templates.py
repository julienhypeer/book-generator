"""
API endpoints for template management and CSS generation.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, Field
from app.services.template_service import (
    TemplateService,
    TemplateConfig,
    PageSettings,
    Typography,
    PrintRules,
)


router = APIRouter(prefix="/api/templates", tags=["templates"])


class PageSettingsRequest(BaseModel):
    """Page settings request model."""

    format: str = Field("156mm 234mm", description="Page format")
    margins: Dict[str, int] = Field(
        default_factory=lambda: {"top": 20, "bottom": 20, "left": 15, "right": 15},
        description="Page margins in mm",
    )
    bleed: int = Field(3, description="Bleed in mm for printing")
    binding_offset: int = Field(0, description="Extra margin for binding")


class TypographyRequest(BaseModel):
    """Typography settings request model."""

    font_family: str = Field("Garamond, Georgia, serif", description="Font family")
    font_size: str = Field("11pt", description="Font size")
    line_height: float = Field(1.6, description="Line height")
    text_align: str = Field("justify", description="Text alignment")
    hyphenation: bool = Field(True, description="Enable hyphenation")
    language: str = Field("en", description="Language code")
    paragraph_indent: str = Field("0", description="Paragraph indent")
    drop_caps: bool = Field(False, description="Enable drop caps")
    quotes_style: str = Field("auto", description="Quotes style")
    spacing_rules: str = Field("auto", description="Spacing rules")


class PrintRulesRequest(BaseModel):
    """Print rules request model."""

    page_numbers: bool = Field(True, description="Show page numbers")
    page_number_position: str = Field(
        "bottom-center", description="Page number position"
    )
    page_number_format: str = Field("decimal", description="Page number format")
    running_headers: bool = Field(False, description="Show running headers")
    header_content: str = Field("chapter", description="Header content type")
    chapter_start: str = Field("auto", description="Chapter start position")
    blank_pages: str = Field("auto", description="Blank pages handling")
    orphans: int = Field(3, description="Minimum orphan lines")
    widows: int = Field(3, description="Minimum widow lines")


class TemplateRequest(BaseModel):
    """Template configuration request."""

    template_name: str = Field("book", description="Template name")
    page_settings: Optional[PageSettingsRequest] = None
    typography: Optional[TypographyRequest] = None
    print_rules: Optional[PrintRulesRequest] = None
    color_scheme: str = Field("blackwhite", description="Color scheme")
    custom_css: str = Field("", description="Custom CSS to add")
    minify: bool = Field(False, description="Minify CSS output")
    use_cache: bool = Field(True, description="Use template cache")
    toc_settings: Dict[str, Any] = Field(
        default_factory=dict, description="TOC settings"
    )
    footnote_settings: Dict[str, Any] = Field(
        default_factory=dict, description="Footnote settings"
    )
    image_settings: Dict[str, Any] = Field(
        default_factory=dict, description="Image settings"
    )
    layout_settings: Dict[str, Any] = Field(
        default_factory=dict, description="Layout settings"
    )
    special_pages: Dict[str, Any] = Field(
        default_factory=dict, description="Special pages settings"
    )
    responsive_print: bool = Field(False, description="Enable responsive print")


class TemplateResponse(BaseModel):
    """Template response model."""

    css: str = Field(..., description="Generated CSS")
    template_name: str = Field(..., description="Template name used")
    minified: bool = Field(..., description="Whether CSS is minified")


class PreviewRequest(BaseModel):
    """Preview request model."""

    template_name: str = Field("book", description="Template to preview")
    sample_content: str = Field("", description="HTML content to preview")
    page_settings: Optional[PageSettingsRequest] = None
    typography: Optional[TypographyRequest] = None


def get_template_service() -> TemplateService:
    """Dependency to get template service instance."""
    return TemplateService()


@router.get("/list")
def list_templates(
    service: TemplateService = Depends(get_template_service),
) -> List[str]:
    """List available templates."""
    return service.available_templates


@router.post("/generate", response_model=TemplateResponse)
def generate_css(
    request: TemplateRequest,
    service: TemplateService = Depends(get_template_service),
) -> TemplateResponse:
    """Generate CSS for a template with custom settings."""
    try:
        # Convert request models to dataclasses
        page_settings = None
        if request.page_settings:
            page_settings = PageSettings(
                format=request.page_settings.format,
                margins=request.page_settings.margins,
                bleed=request.page_settings.bleed,
                binding_offset=request.page_settings.binding_offset,
            )

        typography = None
        if request.typography:
            typography = Typography(
                font_family=request.typography.font_family,
                font_size=request.typography.font_size,
                line_height=request.typography.line_height,
                text_align=request.typography.text_align,
                hyphenation=request.typography.hyphenation,
                language=request.typography.language,
                paragraph_indent=request.typography.paragraph_indent,
                drop_caps=request.typography.drop_caps,
                quotes_style=request.typography.quotes_style,
                spacing_rules=request.typography.spacing_rules,
            )

        print_rules = None
        if request.print_rules:
            print_rules = PrintRules(
                page_numbers=request.print_rules.page_numbers,
                page_number_position=request.print_rules.page_number_position,
                page_number_format=request.print_rules.page_number_format,
                running_headers=request.print_rules.running_headers,
                header_content=request.print_rules.header_content,
                chapter_start=request.print_rules.chapter_start,
                blank_pages=request.print_rules.blank_pages,
                orphans=request.print_rules.orphans,
                widows=request.print_rules.widows,
            )

        config = TemplateConfig(
            template_name=request.template_name,
            page_settings=page_settings,
            typography=typography,
            print_rules=print_rules,
            color_scheme=request.color_scheme,
            custom_css=request.custom_css,
            minify=request.minify,
            use_cache=request.use_cache,
            toc_settings=request.toc_settings,
            footnote_settings=request.footnote_settings,
            image_settings=request.image_settings,
            layout_settings=request.layout_settings,
            special_pages=request.special_pages,
            responsive_print=request.responsive_print,
        )

        css = service.generate_css(config)

        return TemplateResponse(
            css=css,
            template_name=request.template_name,
            minified=request.minify,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
def preview_template(
    request: PreviewRequest,
    service: TemplateService = Depends(get_template_service),
) -> str:
    """Generate HTML preview with template CSS."""
    try:
        # Convert request models to dataclasses
        page_settings = None
        if request.page_settings:
            page_settings = PageSettings(
                format=request.page_settings.format,
                margins=request.page_settings.margins,
                bleed=request.page_settings.bleed,
            )

        typography = None
        if request.typography:
            typography = Typography(
                font_family=request.typography.font_family,
                font_size=request.typography.font_size,
                line_height=request.typography.line_height,
                text_align=request.typography.text_align,
                hyphenation=request.typography.hyphenation,
                language=request.typography.language,
            )

        config = TemplateConfig(
            template_name=request.template_name,
            page_settings=page_settings,
            typography=typography,
        )

        preview_html = service.generate_preview(config, request.sample_content)

        return preview_html

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_name}/css")
def get_template_css(
    template_name: str,
    minify: bool = False,
    service: TemplateService = Depends(get_template_service),
) -> Response:
    """Get CSS for a specific template."""
    try:
        config = TemplateConfig(
            template_name=template_name,
            minify=minify,
        )

        css = service.generate_css(config)

        return Response(
            content=css,
            media_type="text/css",
            headers={"Content-Disposition": f"inline; filename={template_name}.css"},
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets")
def get_template_presets() -> Dict[str, Any]:
    """Get predefined template presets."""
    return {
        "book": {
            "description": "Standard book format for novels and non-fiction",
            "page_format": "156mm 234mm",
            "font": "Garamond",
            "line_height": 1.6,
            "suitable_for": ["novels", "non-fiction", "memoirs", "biographies"],
        },
        "academic": {
            "description": "Academic format for thesis and research papers",
            "page_format": "A4",
            "font": "Times New Roman",
            "line_height": 2.0,
            "suitable_for": ["thesis", "dissertations", "research papers", "reports"],
        },
        "novel": {
            "description": "US Trade Paperback format for fiction",
            "page_format": "5.5in 8.5in",
            "font": "Baskerville",
            "line_height": 1.5,
            "suitable_for": ["fiction", "short stories", "poetry", "creative writing"],
        },
        "technical": {
            "description": "Technical documentation format",
            "page_format": "A4",
            "font": "Arial",
            "line_height": 1.4,
            "suitable_for": ["manuals", "documentation", "guides", "tutorials"],
        },
        "simple": {
            "description": "Minimal format for basic documents",
            "page_format": "A4",
            "font": "System default",
            "line_height": 1.5,
            "suitable_for": ["drafts", "simple documents", "quick exports"],
        },
    }


@router.post("/validate")
def validate_template_config(request: TemplateRequest) -> Dict[str, Any]:
    """Validate template configuration without generating CSS."""
    try:
        # Check template name
        service = TemplateService()
        if request.template_name not in service.available_templates:
            return {
                "valid": False,
                "errors": [f"Invalid template name: {request.template_name}"],
            }

        errors = []
        warnings = []

        # Validate page format
        if request.page_settings:
            format_str = request.page_settings.format
            if (
                format_str not in service.PAGE_FORMATS
                and not service._validate_page_format(format_str)
            ):
                errors.append(f"Invalid page format: {format_str}")

            # Check margins
            margins = request.page_settings.margins
            if any(m < 0 for m in margins.values()):
                errors.append("Margins cannot be negative")
            if any(m > 100 for m in margins.values()):
                warnings.append("Very large margins detected (>100mm)")

        # Validate typography
        if request.typography:
            if request.typography.line_height < 1:
                errors.append("Line height should be >= 1")
            if request.typography.line_height > 3:
                warnings.append("Very large line height (>3)")

            if request.typography.orphans < 1:
                errors.append("Orphans should be >= 1")
            if request.typography.widows < 1:
                errors.append("Widows should be >= 1")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)],
        }


@router.delete("/cache")
def clear_template_cache(
    service: TemplateService = Depends(get_template_service),
) -> Dict[str, str]:
    """Clear template cache."""
    service.clear_cache()
    return {"message": "Template cache cleared successfully"}

"""
API endpoints for markdown processing.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.services.markdown_processor import MarkdownProcessor, MarkdownConfig


router = APIRouter(prefix="/api/markdown", tags=["markdown"])


class MarkdownRequest(BaseModel):
    """Request model for markdown conversion."""

    content: str = Field(..., description="Markdown content to convert")
    enable_toc: bool = Field(True, description="Enable table of contents generation")
    enable_footnotes: bool = Field(True, description="Enable footnotes")
    enable_tables: bool = Field(True, description="Enable tables")
    enable_math: bool = Field(False, description="Enable math/LaTeX support")
    enable_smarty: bool = Field(False, description="Enable smart typography")
    language: str = Field("en", description="Language for typography rules")
    sanitize_html: bool = Field(True, description="Sanitize HTML output")
    template: Optional[str] = Field(None, description="Template name to use")


class MarkdownResponse(BaseModel):
    """Response model for markdown conversion."""

    html: str = Field(..., description="Converted HTML content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extracted metadata"
    )


class BatchMarkdownRequest(BaseModel):
    """Request model for batch markdown conversion."""

    chapters: list[Dict[str, Any]] = Field(
        ..., description="List of chapters to convert"
    )
    config: Optional[MarkdownRequest] = Field(
        None, description="Conversion configuration"
    )


def get_markdown_processor() -> MarkdownProcessor:
    """Dependency to get markdown processor instance."""
    return MarkdownProcessor()


@router.post("/convert", response_model=MarkdownResponse)
def convert_markdown(
    request: MarkdownRequest,
    processor: MarkdownProcessor = Depends(get_markdown_processor),
) -> MarkdownResponse:
    """Convert markdown to HTML with specified configuration."""
    try:
        config = MarkdownConfig(
            enable_toc=request.enable_toc,
            enable_footnotes=request.enable_footnotes,
            enable_tables=request.enable_tables,
            enable_math=request.enable_math,
            enable_smarty=request.enable_smarty,
            language=request.language,
            sanitize_html=request.sanitize_html,
        )

        html, metadata = processor.convert_with_metadata(request.content, config)

        # If template is specified, render with template
        if request.template:
            context = {
                "content": html,
                "title": metadata.get("title", "Document"),
                "author": metadata.get("author", ""),
                "lang": request.language,
                **metadata,
            }
            html = processor.render_template(request.template, context)

        return MarkdownResponse(html=html, metadata=metadata)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=list[MarkdownResponse])
def batch_convert_markdown(
    request: BatchMarkdownRequest,
    processor: MarkdownProcessor = Depends(get_markdown_processor),
) -> list[MarkdownResponse]:
    """Batch convert multiple markdown chapters."""
    try:
        config = None
        if request.config:
            config = MarkdownConfig(
                enable_toc=request.config.enable_toc,
                enable_footnotes=request.config.enable_footnotes,
                enable_tables=request.config.enable_tables,
                enable_math=request.config.enable_math,
                enable_smarty=request.config.enable_smarty,
                language=request.config.language,
                sanitize_html=request.config.sanitize_html,
            )

        results = processor.batch_convert(request.chapters, config)

        responses = []
        for result in results:
            responses.append(
                MarkdownResponse(html=result["html"], metadata={"id": result["id"]})
            )

        return responses

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preview")
def preview_with_template(
    content: str,
    template: str = "book.html",
    title: str = "Preview",
    author: str = "",
    processor: MarkdownProcessor = Depends(get_markdown_processor),
) -> str:
    """Preview markdown with a specific template."""
    try:
        config = MarkdownConfig()
        html, metadata = processor.convert_with_metadata(content, config)

        context = {
            "content": html,
            "title": title,
            "author": author,
            "chapter_title": metadata.get("title", "Chapter"),
            "lang": "en",
            "show_chapter_title": True,
            "toc": False,
            "page_numbers": True,
            **metadata,
        }

        rendered = processor.render_template(template, context)
        return rendered

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates")
def list_templates() -> list[str]:
    """List available templates."""
    from pathlib import Path

    template_dir = Path(__file__).parent.parent / "templates"
    if not template_dir.exists():
        return []

    templates = []
    for template_file in template_dir.glob("*.html"):
        templates.append(template_file.name)

    return templates

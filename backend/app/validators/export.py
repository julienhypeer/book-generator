"""
Validators for export endpoints.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ExportFormat(str, Enum):
    """Supported export formats."""
    PDF = "pdf"
    HTML = "html"
    EPUB = "epub"
    DOCX = "docx"


class PageFormat(str, Enum):
    """Standard page formats."""
    BOOK = "156mm 234mm"  # Standard book format
    A4 = "210mm 297mm"
    A5 = "148mm 210mm"
    LETTER = "8.5in 11in"
    CUSTOM = "custom"


class ExportConfig(BaseModel):
    """Configuration for PDF export."""
    
    # Format settings
    format: ExportFormat = Field(default=ExportFormat.PDF)
    page_format: PageFormat = Field(default=PageFormat.BOOK)
    
    # Custom dimensions (if page_format is CUSTOM)
    custom_width: Optional[str] = Field(None, description="Custom width (e.g., '170mm')")
    custom_height: Optional[str] = Field(None, description="Custom height (e.g., '240mm')")
    
    # Margins (in mm)
    margins: Dict[str, int] = Field(
        default_factory=lambda: {
            "top": 20,
            "bottom": 20,
            "left": 15,
            "right": 15,
            "gutter": 10  # Additional margin for binding
        }
    )
    
    # Typography
    font_family: str = Field(default="Georgia, serif")
    font_size: int = Field(default=11, ge=8, le=16)
    line_height: float = Field(default=1.6, ge=1.0, le=2.5)
    
    # Template
    template: str = Field(default="professional")
    
    # Content options
    include_toc: bool = Field(default=True, description="Include table of contents")
    include_page_numbers: bool = Field(default=True)
    include_header: bool = Field(default=True)
    include_footer: bool = Field(default=True)
    
    # Language and localization
    language: str = Field(default="fr", description="Language code (fr, en, etc.)")
    
    # Advanced options
    enable_math: bool = Field(default=False, description="Enable math rendering")
    enable_hyphenation: bool = Field(default=True)
    orphans: int = Field(default=3, ge=1, le=5)
    widows: int = Field(default=3, ge=1, le=5)
    
    @validator("custom_width", "custom_height")
    def validate_custom_dimensions(cls, v, values):
        """Validate custom dimensions when page_format is CUSTOM."""
        if values.get("page_format") == PageFormat.CUSTOM and not v:
            raise ValueError("Custom dimensions required when page_format is CUSTOM")
        return v
    
    class Config:
        use_enum_values = True


class ExportResponse(BaseModel):
    """Response for export operations."""
    
    success: bool
    message: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    generation_time: Optional[float] = None


class PreviewConfig(BaseModel):
    """Configuration for export preview."""
    
    format: ExportFormat = Field(default=ExportFormat.HTML)
    max_chapters: int = Field(default=3, ge=1, le=10)
    include_css: bool = Field(default=True)
    include_toc: bool = Field(default=True)
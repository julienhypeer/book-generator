"""Export validators for PDF generation requests."""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict, Any, List
from enum import Enum


class ExportFormat(str, Enum):
    """Supported export formats."""
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    DOCX = "docx"
    EPUB = "epub"


class TemplateType(str, Enum):
    """Available book templates."""
    ROMAN = "roman"
    TECHNICAL = "technical"
    ACADEMIC = "academic"


class PaperSize(str, Enum):
    """Supported paper sizes."""
    A4 = "a4"
    LETTER = "letter"
    BOOK = "book"  # 156mm x 234mm standard book format


class ExportRequest(BaseModel):
    """Request model for PDF/document export."""
    
    format: ExportFormat = Field(
        default=ExportFormat.PDF,
        description="Output format for the export"
    )
    
    template: TemplateType = Field(
        default=TemplateType.ROMAN,
        description="Template style to apply"
    )
    
    paper_size: PaperSize = Field(
        default=PaperSize.BOOK,
        description="Paper size for the document"
    )
    
    include_toc: bool = Field(
        default=True,
        description="Include table of contents"
    )
    
    include_page_numbers: bool = Field(
        default=True,
        description="Include page numbering"
    )
    
    quality_validation: bool = Field(
        default=True,
        description="Perform quality checks (6 critical issues)"
    )
    
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional format-specific options"
    )
    
    @validator('options')
    def validate_options(cls, v, values):
        """Validate format-specific options."""
        if v is None:
            return {}
        
        format_type = values.get('format')
        
        if format_type == ExportFormat.PDF:
            allowed_keys = {
                'font_size', 'line_height', 'margins', 
                'hyphenation', 'quality_checks'
            }
            if not all(key in allowed_keys for key in v.keys()):
                invalid_keys = set(v.keys()) - allowed_keys
                raise ValueError(f"Invalid PDF options: {invalid_keys}")
        
        return v


class ExportResponse(BaseModel):
    """Response model for export operations."""
    
    success: bool = Field(description="Whether export was successful")
    
    format: ExportFormat = Field(description="Export format used")
    
    file_size: Optional[int] = Field(
        default=None,
        description="Size of generated file in bytes"
    )
    
    page_count: Optional[int] = Field(
        default=None,
        description="Number of pages (for PDF)"
    )
    
    quality_report: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Quality validation results"
    )
    
    generation_time: Optional[float] = Field(
        default=None,
        description="Time taken to generate in seconds"
    )
    
    warnings: Optional[List[str]] = Field(
        default=None,
        description="Non-critical warnings during generation"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the export"
    )


class QualityValidationResult(BaseModel):
    """Quality validation result for PDF exports."""
    
    check_name: str = Field(description="Name of quality check")
    
    passed: bool = Field(description="Whether check passed")
    
    severity: Literal["info", "warning", "error"] = Field(
        description="Severity level"
    )
    
    message: str = Field(description="Human readable message")
    
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional details about the check"
    )


class QualityReport(BaseModel):
    """Complete quality report for PDF generation."""
    
    overall_score: Literal["PASS", "ISSUES", "FAIL"] = Field(
        description="Overall quality assessment"
    )
    
    checks_performed: int = Field(
        description="Number of quality checks performed"
    )
    
    checks_passed: int = Field(
        description="Number of checks that passed"
    )
    
    results: List[QualityValidationResult] = Field(
        description="Detailed results for each check"
    )
    
    critical_issues: List[str] = Field(
        description="List of critical issues found"
    )
    
    recommendations: List[str] = Field(
        description="Recommendations for improvement"
    )
    
    generation_metadata: Dict[str, Any] = Field(
        description="Technical metadata about generation process"
    )


class ExportJobStatus(str, Enum):
    """Status of export job."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportJob(BaseModel):
    """Export job tracking model."""
    
    job_id: str = Field(description="Unique job identifier")
    
    project_id: int = Field(description="Project being exported")
    
    status: ExportJobStatus = Field(description="Current job status")
    
    format: ExportFormat = Field(description="Export format")
    
    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Progress percentage (0-100)"
    )
    
    started_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when job started"
    )
    
    completed_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when job completed"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if job failed"
    )
    
    result: Optional[ExportResponse] = Field(
        default=None,
        description="Export result when completed"
    )
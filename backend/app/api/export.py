"""Export API endpoints for PDF generation."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response
from typing import Dict, Any
import logging
from pathlib import Path

from app.core.database import get_db
from app.services.project import ProjectService
from app.services.chapter import ChapterService
from app.services.pdf_generator import AdvancedPDFGenerator
from app.validators.export import ExportRequest, ExportResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/export", tags=["export"])
logger = logging.getLogger(__name__)


@router.post("/{project_id}/pdf", response_model=ExportResponse)
async def export_project_pdf(
    project_id: int,
    export_request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Response:
    """
    Export project as professional-quality PDF with advanced pagination.
    
    Résout les 6 problèmes critiques:
    1. Pages blanches parasites
    2. Espacement entre mots/rivières  
    3. Correspondance TOC
    4. Gestion sous-parties
    5. Barres horizontales parasites
    6. Titres orphelins
    """
    try:
        # Get project and chapters
        project_service = ProjectService(db)
        chapter_service = ChapterService(db)
        
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        chapters = chapter_service.get_chapters_by_project(project_id)
        if not chapters:
            raise HTTPException(status_code=400, detail="No chapters found in project")
        
        # Generate PDF with advanced pagination
        pdf_generator = AdvancedPDFGenerator()
        
        logger.info(f"Starting PDF export for project {project_id} ({len(chapters)} chapters)")
        
        pdf_bytes, metadata = await pdf_generator.generate_from_project(
            project, chapters
        )
        
        # Validate quality
        quality_report = metadata.get('quality_validation', {})
        all_checks_passed = metadata.get('all_checks_passed', False)
        
        if not all_checks_passed:
            logger.warning(f"PDF quality issues detected for project {project_id}")
            for check_name, result in quality_report.items():
                if not result.get('valid', True):
                    logger.warning(f"  - {check_name}: {result}")
        
        # Prepare response headers
        headers = {
            "Content-Type": "application/pdf",
            "Content-Disposition": f'attachment; filename="{project.title}.pdf"',
            "X-Page-Count": str(metadata['page_count']),
            "X-Quality-Score": "PASS" if all_checks_passed else "ISSUES",
            "X-Generation-Method": "double-pass-advanced"
        }
        
        # Add quality details to headers
        for check_name, result in quality_report.items():
            status = "OK" if result.get('valid', True) else "FAIL"
            headers[f"X-Quality-{check_name.title()}"] = status
        
        logger.info(
            f"PDF export completed for project {project_id}: "
            f"{metadata['page_count']} pages, "
            f"quality={'PASS' if all_checks_passed else 'ISSUES'}"
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"PDF export failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/{project_id}/pdf/validate")
async def validate_pdf_quality(
    project_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate PDF quality without generating full document.
    Used for pre-export quality checks.
    """
    try:
        # Get project data
        project_service = ProjectService(db)
        chapter_service = ChapterService(db)
        
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        chapters = chapter_service.get_chapters_by_project(project_id)
        if not chapters:
            raise HTTPException(status_code=400, detail="No chapters found")
        
        # Quick validation analysis
        issues = []
        warnings = []
        
        # Check chapter count
        if len(chapters) > 100:
            warnings.append("Large document (>100 chapters) - generation may take longer")
        
        # Check content length
        total_chars = sum(len(chapter.content or '') for chapter in chapters)
        if total_chars > 500000:  # 500K chars ≈ 400 pages
            warnings.append("Large content - memory usage may be high")
        
        # Check for problematic HTML patterns
        for chapter in chapters:
            content = chapter.content or ''
            
            # Detect <hr> tags (cause horizontal bars)
            if '<hr' in content:
                issues.append(f"Chapter '{chapter.title}' contains <hr> tags - will cause horizontal bars")
            
            # Detect very long paragraphs (cause rivers)
            if len(content.replace(' ', '')) > 5000:
                warnings.append(f"Chapter '{chapter.title}' has very long paragraphs - may cause text rivers")
        
        # Estimate page count
        estimated_pages = max(1, total_chars // 1200)  # Rough estimate
        
        severity = "error" if issues else ("warning" if warnings else "ok")
        
        return {
            "project_id": project_id,
            "severity": severity,
            "estimated_pages": estimated_pages,
            "chapter_count": len(chapters),
            "total_characters": total_chars,
            "issues": issues,
            "warnings": warnings,
            "recommendations": [
                "Use markdown separators instead of <hr> tags",
                "Break very long paragraphs for better readability",
                "Ensure chapter titles are descriptive for TOC",
                "Test with small projects first"
            ] if issues or warnings else []
        }
        
    except Exception as e:
        logger.error(f"PDF validation failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/quality-report")
async def get_quality_standards() -> Dict[str, Any]:
    """
    Get the quality standards and checks applied to PDF generation.
    """
    return {
        "version": "2.0",
        "quality_checks": {
            "blank_pages": {
                "description": "Detect parasitic blank pages vs editorial pages",
                "criteria": "Zero unintentional blank pages",
                "method": "Page content analysis with editorial context"
            },
            "text_rivers": {
                "description": "Detect white rivers in justified text",
                "criteria": "Minimal word spacing irregularities",
                "method": "Word density analysis in long paragraphs"
            },
            "toc_sync": {
                "description": "Ensure TOC page numbers match actual content",
                "criteria": "100% accuracy between TOC and actual pages",
                "method": "Two-pass generation with position mapping"
            },
            "orphan_titles": {
                "description": "Prevent titles alone at bottom of page",
                "criteria": "Minimum 3 lines of content after each title",
                "method": "Page position analysis with orphan detection"
            }
        },
        "technical_standards": {
            "page_format": "156mm x 234mm (standard book format)",
            "margins": "20mm top/bottom, 15mm left/right",
            "typography": "Crimson Text, 11pt, 1.7 line height",
            "hyphenation": "French rules, 6-3-3 character limits",
            "pagination": "Bottom center, professional numbering"
        },
        "generation_method": "Two-pass WeasyPrint with quality validation",
        "supported_features": [
            "Automatic TOC generation",
            "Chapter numbering",
            "French hyphenation",
            "Orphan/widow prevention",
            "Professional typography",
            "Quality validation"
        ]
    }
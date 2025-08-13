"""Preview API endpoints for book preview generation."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db_session
from app.services.project_service import ProjectService
from app.services.chapter_service import ChapterService
from app.services.markdown_processor import MarkdownProcessor

router = APIRouter(prefix="/api/projects", tags=["preview"])
logger = logging.getLogger(__name__)


@router.get("/{project_id}/preview")
async def get_project_preview(
    project_id: int,
    template: str = "roman",
    db: Session = Depends(get_db_session)
) -> HTMLResponse:
    """
    Generate HTML preview for a project.
    
    Returns HTML content that can be displayed in an iframe.
    """
    try:
        # Get project and chapters
        project_service = ProjectService(db)
        chapter_service = ChapterService(db)
        
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        chapters = chapter_service.list_chapters(project_id)
        
        # Combine chapter content
        markdown_content = ""
        for chapter in chapters:
            markdown_content += f"# {chapter.title}\n\n{chapter.content}\n\n"
        
        # Process markdown to HTML
        processor = MarkdownProcessor()
        html_content = processor.convert(markdown_content)
        
        # Apply basic template
        full_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{project.title}</title>
            <style>
                body {{
                    font-family: 'Georgia', serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px 20px;
                    line-height: 1.8;
                    color: #333;
                    background: #fff;
                }}
                h1 {{
                    font-size: 2.5em;
                    margin: 2em 0 1em 0;
                    text-align: center;
                    color: #222;
                    page-break-before: always;
                }}
                h2 {{
                    font-size: 1.8em;
                    margin: 1.5em 0 0.5em 0;
                    color: #444;
                }}
                h3 {{
                    font-size: 1.4em;
                    margin: 1.2em 0 0.4em 0;
                    color: #555;
                }}
                p {{
                    text-align: justify;
                    margin-bottom: 1em;
                }}
                blockquote {{
                    margin: 1.5em 2em;
                    padding-left: 1em;
                    border-left: 3px solid #ddd;
                    font-style: italic;
                    color: #666;
                }}
                code {{
                    background: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.95em;
                }}
                pre {{
                    background: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                .title-page {{
                    text-align: center;
                    margin-bottom: 4em;
                    padding: 2em 0;
                    border-bottom: 1px solid #ddd;
                }}
                .author {{
                    font-size: 1.2em;
                    color: #666;
                    margin-top: 1em;
                }}
            </style>
        </head>
        <body>
            <div class="title-page">
                <h1 style="page-break-before: avoid;">{project.title}</h1>
                <div class="author">par {project.author or "Unknown Author"}</div>
            </div>
            {html_content}
        </body>
        </html>
        """
        
        logger.info(f"Generated preview for project {project_id}")
        
        return HTMLResponse(content=full_html)
        
    except Exception as e:
        logger.error(f"Preview generation failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")
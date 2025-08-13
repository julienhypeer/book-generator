"""API endpoints for Chapter management."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.services.chapter_service import ChapterService
from app.validators.chapter import (
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    BulkChapterReorder,
)

router = APIRouter(prefix="/api/projects/{project_id}/chapters", tags=["chapters"])


def get_chapter_service(db: Session = Depends(get_db_session)) -> ChapterService:
    """Dependency to get ChapterService instance."""
    return ChapterService(db)


# Create chapter endpoint
@router.post("", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(
    project_id: int,
    chapter_data: ChapterCreate,
    service: ChapterService = Depends(get_chapter_service),
) -> ChapterResponse:
    """Create a new chapter for a project."""
    try:
        chapter = service.create_chapter(project_id, chapter_data)
        return ChapterResponse.model_validate(chapter)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# List chapters endpoint
@router.get("", response_model=List[ChapterResponse])
def list_chapters(
    project_id: int,
    service: ChapterService = Depends(get_chapter_service),
) -> List[ChapterResponse]:
    """List all chapters for a project."""
    chapters = service.list_chapters(project_id)
    return [ChapterResponse.model_validate(ch) for ch in chapters]


# Export all chapters endpoint (must be before /{chapter_id} routes)
@router.get("/export")
def export_all_chapters(
    project_id: int,
    include_metadata: bool = False,
    service: ChapterService = Depends(get_chapter_service),
) -> Response:
    """Export all chapters as a single Markdown file."""
    markdown = service.export_all_chapters(project_id, include_metadata)
    return Response(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=project_{project_id}_chapters.md"
        },
    )


# Import single chapter endpoint
@router.post(
    "/import", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED
)
async def import_chapter(
    project_id: int,
    request: Request,
    service: ChapterService = Depends(get_chapter_service),
) -> ChapterResponse:
    """Import a chapter from Markdown."""
    try:
        markdown_content = await request.body()
        markdown_content = markdown_content.decode("utf-8")
        chapter = service.import_chapter_markdown(project_id, markdown_content)
        return ChapterResponse.model_validate(chapter)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Import bulk chapters endpoint
@router.post(
    "/import/bulk",
    response_model=List[ChapterResponse],
    status_code=status.HTTP_201_CREATED,
)
async def import_bulk_chapters(
    project_id: int,
    request: Request,
    service: ChapterService = Depends(get_chapter_service),
) -> List[ChapterResponse]:
    """Import multiple chapters from a single Markdown document."""
    try:
        markdown_content = await request.body()
        markdown_content = markdown_content.decode("utf-8")
        chapters = service.import_bulk_markdown(project_id, markdown_content)
        return [ChapterResponse.model_validate(ch) for ch in chapters]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Reorder chapters endpoint
@router.post("/reorder", response_model=List[ChapterResponse])
def reorder_chapters(
    project_id: int,
    reorder_data: BulkChapterReorder,
    service: ChapterService = Depends(get_chapter_service),
) -> List[ChapterResponse]:
    """Bulk reorder chapters."""
    try:
        chapters = service.bulk_reorder_chapters(project_id, reorder_data)
        return [ChapterResponse.model_validate(ch) for ch in chapters]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Get specific chapter endpoint
@router.get("/{chapter_id}", response_model=ChapterResponse)
def get_chapter(
    project_id: int,
    chapter_id: int,
    service: ChapterService = Depends(get_chapter_service),
) -> ChapterResponse:
    """Get a specific chapter."""
    chapter = service.get_chapter(project_id, chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found"
        )
    return ChapterResponse.model_validate(chapter)


# Update chapter endpoint
@router.patch("/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    project_id: int,
    chapter_id: int,
    chapter_data: ChapterUpdate,
    service: ChapterService = Depends(get_chapter_service),
) -> ChapterResponse:
    """Update a chapter."""
    chapter = service.update_chapter(project_id, chapter_id, chapter_data)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found"
        )
    return ChapterResponse.model_validate(chapter)


# Delete chapter endpoint
@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(
    project_id: int,
    chapter_id: int,
    service: ChapterService = Depends(get_chapter_service),
) -> None:
    """Delete a chapter."""
    success = service.delete_chapter(project_id, chapter_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found"
        )


# Export single chapter endpoint
@router.get("/{chapter_id}/export")
def export_chapter(
    project_id: int,
    chapter_id: int,
    include_metadata: bool = False,
    service: ChapterService = Depends(get_chapter_service),
) -> Response:
    """Export a chapter as Markdown."""
    try:
        markdown = service.export_chapter_markdown(
            project_id, chapter_id, include_metadata
        )
        return Response(
            content=markdown,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=chapter_{chapter_id}.md"
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

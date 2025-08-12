"""Service layer for Chapter operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Chapter, Project
from app.validators.chapter import (
    ChapterCreate,
    ChapterUpdate,
    BulkChapterReorder,
)


class ChapterService:
    """Service for managing chapters."""

    def __init__(self, db: Session):
        """Initialize ChapterService with database session."""
        self.db = db

    def create_chapter(self, project_id: int, chapter_data: ChapterCreate) -> Chapter:
        """Create a new chapter for a project."""
        # Verify project exists
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with id {project_id} not found")

        # Auto-assign position if not provided
        position = chapter_data.position
        if position is None:
            # Get the max position for this project
            max_position = (
                self.db.query(Chapter).filter(Chapter.project_id == project_id).count()
            )
            position = max_position + 1

        # Create chapter
        chapter = Chapter(
            project_id=project_id,
            title=chapter_data.title,
            content=chapter_data.content,
            position=position,
        )

        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)

        return chapter

    def get_chapter(self, project_id: int, chapter_id: int) -> Optional[Chapter]:
        """Get a chapter by ID."""
        return (
            self.db.query(Chapter)
            .filter(and_(Chapter.id == chapter_id, Chapter.project_id == project_id))
            .first()
        )

    def list_chapters(self, project_id: int) -> List[Chapter]:
        """List all chapters for a project, ordered by position."""
        return (
            self.db.query(Chapter)
            .filter(Chapter.project_id == project_id)
            .order_by(Chapter.position)
            .all()
        )

    def update_chapter(
        self, project_id: int, chapter_id: int, chapter_data: ChapterUpdate
    ) -> Optional[Chapter]:
        """Update a chapter."""
        chapter = self.get_chapter(project_id, chapter_id)
        if not chapter:
            return None

        # Handle position change (reordering)
        if (
            chapter_data.position is not None
            and chapter_data.position != chapter.position
        ):
            self._reorder_chapters(project_id, chapter_id, chapter_data.position)

        # Update other fields
        update_data = chapter_data.model_dump(exclude_unset=True, exclude={"position"})
        for field, value in update_data.items():
            setattr(chapter, field, value)

        self.db.commit()
        self.db.refresh(chapter)

        return chapter

    def delete_chapter(self, project_id: int, chapter_id: int) -> bool:
        """Delete a chapter and reorder remaining chapters."""
        chapter = self.get_chapter(project_id, chapter_id)
        if not chapter:
            return False

        deleted_position = chapter.position

        # Delete the chapter
        self.db.delete(chapter)
        self.db.commit()

        # Reorder remaining chapters
        remaining_chapters = (
            self.db.query(Chapter)
            .filter(
                and_(
                    Chapter.project_id == project_id,
                    Chapter.position > deleted_position,
                )
            )
            .all()
        )

        for ch in remaining_chapters:
            ch.position -= 1

        self.db.commit()

        return True

    def _reorder_chapters(
        self, project_id: int, chapter_id: int, new_position: int
    ) -> None:
        """Reorder chapters when one is moved."""
        chapter = self.get_chapter(project_id, chapter_id)
        if not chapter:
            return

        old_position = chapter.position

        if old_position == new_position:
            return

        # Get all chapters that need to be reordered
        if new_position < old_position:
            # Moving up - shift others down
            affected_chapters = (
                self.db.query(Chapter)
                .filter(
                    and_(
                        Chapter.project_id == project_id,
                        Chapter.position >= new_position,
                        Chapter.position < old_position,
                        Chapter.id != chapter_id,
                    )
                )
                .all()
            )
            for ch in affected_chapters:
                ch.position += 1
        else:
            # Moving down - shift others up
            affected_chapters = (
                self.db.query(Chapter)
                .filter(
                    and_(
                        Chapter.project_id == project_id,
                        Chapter.position > old_position,
                        Chapter.position <= new_position,
                        Chapter.id != chapter_id,
                    )
                )
                .all()
            )
            for ch in affected_chapters:
                ch.position -= 1

        # Update the moved chapter's position
        chapter.position = new_position
        self.db.commit()

    def bulk_reorder_chapters(
        self, project_id: int, reorder_data: BulkChapterReorder
    ) -> List[Chapter]:
        """Bulk reorder multiple chapters."""
        # Verify all chapters belong to the project
        chapter_ids = [ch.chapter_id for ch in reorder_data.chapters]
        chapters = (
            self.db.query(Chapter)
            .filter(and_(Chapter.project_id == project_id, Chapter.id.in_(chapter_ids)))
            .all()
        )

        if len(chapters) != len(chapter_ids):
            raise ValueError("Some chapters not found or don't belong to project")

        # Apply new positions
        for reorder_item in reorder_data.chapters:
            chapter = next(
                (ch for ch in chapters if ch.id == reorder_item.chapter_id), None
            )
            if chapter:
                chapter.position = reorder_item.new_position

        self.db.commit()

        # Return updated chapters in order
        return self.list_chapters(project_id)

    def export_chapter_markdown(
        self, project_id: int, chapter_id: int, include_metadata: bool = False
    ) -> str:
        """Export a chapter as Markdown."""
        chapter = self.get_chapter(project_id, chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        markdown = f"# {chapter.title}\n\n"

        if include_metadata:
            markdown += f"<!-- Position: {chapter.position} -->\n"
            markdown += f"<!-- Created: {chapter.created_at.isoformat()} -->\n"
            markdown += f"<!-- Updated: {chapter.updated_at.isoformat()} -->\n\n"

        markdown += chapter.content

        return markdown

    def export_all_chapters_markdown(
        self, project_id: int, include_metadata: bool = False
    ) -> str:
        """Export all chapters as a single Markdown document."""
        chapters = self.list_chapters(project_id)

        if not chapters:
            return ""

        markdown_parts = []
        for chapter in chapters:
            markdown_parts.append(
                self.export_chapter_markdown(project_id, chapter.id, include_metadata)
            )

        return "\n\n---\n\n".join(markdown_parts)

    def import_chapter_markdown(
        self, project_id: int, markdown_content: str
    ) -> Chapter:
        """Import a chapter from Markdown content."""
        # Verify project exists
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with id {project_id} not found")

        # Extract title from first H1
        lines = markdown_content.strip().split("\n")
        title = None
        content_lines = []

        for i, line in enumerate(lines):
            if line.startswith("# ") and title is None:
                title = line[2:].strip()
            else:
                content_lines.append(line)

        if not title:
            raise ValueError("Markdown must contain a title (H1 heading)")

        content = "\n".join(content_lines).strip()

        # Create chapter with extracted data
        chapter_data = ChapterCreate(
            title=title,
            content=content,
        )

        return self.create_chapter(project_id, chapter_data)

    def import_bulk_markdown(
        self, project_id: int, markdown_content: str
    ) -> List[Chapter]:
        """Import multiple chapters from a single Markdown document."""
        # Split by horizontal rules
        chapter_sections = markdown_content.split("\n---\n")

        created_chapters = []
        for section in chapter_sections:
            section = section.strip()
            if section:
                try:
                    chapter = self.import_chapter_markdown(project_id, section)
                    created_chapters.append(chapter)
                except ValueError:
                    # Skip sections without proper title
                    continue

        return created_chapters

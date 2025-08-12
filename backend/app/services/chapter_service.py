"""
Chapter service for business logic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.chapter import Chapter
from app.validators.chapter import ChapterCreate, ChapterUpdate


class ChapterService:
    """Service for managing chapters."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    def create_chapter(self, project_id: int, chapter_data: ChapterCreate) -> Chapter:
        """Create a new chapter."""
        # Get next position if not provided
        position = chapter_data.position
        if position is None:
            max_position = self.db.query(Chapter).filter(
                Chapter.project_id == project_id
            ).count()
            position = max_position + 1
        
        chapter = Chapter(
            project_id=project_id,
            title=chapter_data.title,
            content=chapter_data.content or "",
            position=position,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)
        
        return chapter
    
    def get_chapter(self, project_id: int, chapter_id: int) -> Optional[Chapter]:
        """Get a chapter by ID."""
        return self.db.query(Chapter).filter(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id
        ).first()
    
    def list_chapters(self, project_id: int) -> List[Chapter]:
        """List all chapters for a project."""
        return self.db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).order_by(Chapter.position).all()
    
    def update(self, project_id: int, chapter_id: int, data: Dict[str, Any]) -> Optional[Chapter]:
        """Update a chapter."""
        chapter = self.get_chapter(project_id, chapter_id)
        if not chapter:
            return None
        
        for key, value in data.items():
            if hasattr(chapter, key):
                setattr(chapter, key, value)
        
        chapter.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(chapter)
        
        return chapter
    
    def delete(self, project_id: int, chapter_id: int) -> bool:
        """Delete a chapter."""
        chapter = self.get_chapter(project_id, chapter_id)
        if not chapter:
            return False
        
        # Update positions of subsequent chapters
        self.db.query(Chapter).filter(
            Chapter.project_id == project_id,
            Chapter.position > chapter.position
        ).update({"position": Chapter.position - 1})
        
        self.db.delete(chapter)
        self.db.commit()
        
        return True
    
    def reorder_chapters(self, project_id: int, chapter_ids: List[int]) -> bool:
        """Reorder chapters by providing new order of IDs."""
        chapters = self.db.query(Chapter).filter(
            Chapter.project_id == project_id,
            Chapter.id.in_(chapter_ids)
        ).all()
        
        if len(chapters) != len(chapter_ids):
            return False
        
        # Update positions based on new order
        for index, chapter_id in enumerate(chapter_ids):
            chapter = next((c for c in chapters if c.id == chapter_id), None)
            if chapter:
                chapter.position = index + 1
        
        self.db.commit()
        return True
    
    def import_chapter_markdown(self, project_id: int, markdown_content: str) -> Chapter:
        """Import a chapter from markdown content."""
        # Extract title from first H1 heading
        lines = markdown_content.strip().split('\n')
        title = "Untitled Chapter"
        content = markdown_content
        
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                # Remove title from content
                content = '\n'.join(lines[lines.index(line)+1:]).strip()
                break
        
        # Create chapter data
        chapter_data = ChapterCreate(
            title=title,
            content=content
        )
        
        return self.create_chapter(project_id, chapter_data)
    
    def import_bulk_markdown(self, project_id: int, markdown_content: str) -> List[Chapter]:
        """Import multiple chapters from a single markdown document."""
        chapters = []
        current_chapter = None
        current_content = []
        
        lines = markdown_content.strip().split('\n')
        
        for line in lines:
            if line.startswith('# '):
                # Save previous chapter if exists
                if current_chapter:
                    chapter_data = ChapterCreate(
                        title=current_chapter,
                        content='\n'.join(current_content).strip()
                    )
                    chapters.append(self.create_chapter(project_id, chapter_data))
                
                # Start new chapter
                current_chapter = line[2:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last chapter
        if current_chapter:
            chapter_data = ChapterCreate(
                title=current_chapter,
                content='\n'.join(current_content).strip()
            )
            chapters.append(self.create_chapter(project_id, chapter_data))
        
        return chapters
    
    def bulk_reorder_chapters(self, project_id: int, reorder_data) -> List[Chapter]:
        """Reorder chapters based on provided data."""
        # Get all chapters for the project
        chapters = self.get_chapters_by_project(project_id)
        
        # Update positions based on reorder_data
        for item in reorder_data.chapters:
            chapter = next((c for c in chapters if c.id == item['id']), None)
            if chapter:
                chapter.position = item['position']
        
        self.db.commit()
        
        # Return updated chapters sorted by position
        return sorted(chapters, key=lambda x: x.position)
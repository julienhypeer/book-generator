"""Project service for business logic."""

import json
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.project import Project
from app.validators.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project operations."""

    def __init__(self, db: Session):
        """Initialize project service with database session."""
        self.db = db

    def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        # Convert settings dict to JSON string if provided
        settings_json = None
        if project_data.settings:
            settings_json = json.dumps(project_data.settings)

        project = Project(
            title=project_data.title,
            author=project_data.author,
            description=project_data.description,
            settings_json=settings_json,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def list_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """List all projects with pagination."""
        return self.db.query(Project).offset(skip).limit(limit).all()

    def update_project(
        self, project_id: int, project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update a project's metadata."""
        project = self.get_project(project_id)
        if not project:
            return None

        # Update fields if provided
        if project_data.title is not None:
            project.title = project_data.title
        if project_data.author is not None:
            project.author = project_data.author
        if project_data.description is not None:
            project.description = project_data.description
        if project_data.settings is not None:
            project.settings_json = json.dumps(project_data.settings)

        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its chapters."""
        project = self.get_project(project_id)
        if not project:
            return False

        self.db.delete(project)
        self.db.commit()
        return True

    def count_projects(self) -> int:
        """Count total number of projects."""
        return self.db.query(Project).count()

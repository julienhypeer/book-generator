"""Project API endpoints."""

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.services.project_service import ProjectService
from app.validators.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)


router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_project_service(db: Session = Depends(get_db_session)) -> ProjectService:
    """Get project service instance."""
    return ProjectService(db)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Create a new project."""
    project = service.create_project(project_data)

    # Convert settings_json back to dict for response
    settings = None
    if project.settings_json:
        settings = json.loads(project.settings_json)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        author=project.author,
        description=project.description,
        settings=settings,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Get a project by ID."""
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Convert settings_json back to dict for response
    settings = None
    if project.settings_json:
        settings = json.loads(project.settings_json)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        author=project.author,
        description=project.description,
        settings=settings,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    service: ProjectService = Depends(get_project_service),
) -> List[ProjectResponse]:
    """List all projects."""
    projects = service.list_projects(skip=skip, limit=limit)

    result = []
    for project in projects:
        # Convert settings_json back to dict for response
        settings = None
        if project.settings_json:
            settings = json.loads(project.settings_json)

        result.append(
            ProjectResponse(
                id=project.id,
                title=project.title,
                author=project.author,
                description=project.description,
                settings=settings,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )

    return result


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Update a project's metadata."""
    project = service.update_project(project_id, project_data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Convert settings_json back to dict for response
    settings = None
    if project.settings_json:
        settings = json.loads(project.settings_json)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        author=project.author,
        description=project.description,
        settings=settings,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> None:
    """Delete a project."""
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

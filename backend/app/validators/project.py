"""Project validation schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ProjectBase(BaseModel):
    """Base project schema with common fields."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class ProjectCreate(BaseModel):
    """Schema for creating a project."""

    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

    @field_validator("title", "author")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure title and author are not empty strings."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

    @field_validator("title", "author")
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title and author are not empty if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Field cannot be empty")
            return v.strip()
        return v


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: int
    title: str
    author: str
    description: Optional[str]
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Schema for list of projects response."""

    projects: list[ProjectResponse]
    total: int

    model_config = {"from_attributes": True}

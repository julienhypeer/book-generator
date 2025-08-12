"""Pydantic schemas for Chapter validation."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ChapterBase(BaseModel):
    """Base schema for Chapter."""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")
    position: Optional[int] = Field(None, ge=1)


class ChapterCreate(ChapterBase):
    """Schema for creating a Chapter."""

    pass


class ChapterUpdate(BaseModel):
    """Schema for updating a Chapter."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    position: Optional[int] = Field(None, ge=1)


class ChapterResponse(BaseModel):
    """Schema for Chapter response."""

    id: int
    project_id: int
    title: str
    content: str
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterImport(BaseModel):
    """Schema for importing a chapter from Markdown."""

    markdown_content: str = Field(..., min_length=1)

    @field_validator("markdown_content")
    @classmethod
    def extract_title_from_markdown(cls, v: str) -> str:
        """Validate that markdown has a title."""
        lines = v.strip().split("\n")
        if not lines:
            raise ValueError("Markdown content cannot be empty")

        # Look for first heading
        for line in lines:
            if line.startswith("# "):
                return v

        raise ValueError("Markdown must contain at least one H1 heading for title")


class ChapterExport(BaseModel):
    """Schema for exporting a chapter to Markdown."""

    include_metadata: bool = Field(default=False)
    include_position: bool = Field(default=True)


class ChapterReorder(BaseModel):
    """Schema for reordering chapters."""

    chapter_id: int
    new_position: int = Field(..., ge=1)


class BulkChapterReorder(BaseModel):
    """Schema for bulk reordering chapters."""

    chapters: list[ChapterReorder]

    @field_validator("chapters")
    @classmethod
    def validate_unique_positions(cls, v: list[ChapterReorder]) -> list:
        """Ensure all positions are unique."""
        positions = [ch.new_position for ch in v]
        if len(positions) != len(set(positions)):
            raise ValueError("All positions must be unique")
        return v

"""Project model for database."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Project(Base):
    """Project model representing a book project."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # JSON string for project settings
    settings_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    chapters = relationship(
        "Chapter", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Project(id={self.id}, title='{self.title}', "
            f"author='{self.author}')>"
        )

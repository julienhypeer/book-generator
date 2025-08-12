"""Tests for Chapter CRUD API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db_session
from app.main import app

# Import models to register with Base (noqa: F401)
from app.models import Project, Chapter  # noqa: F401


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create test client with test database."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db_session] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_project(client):
    """Create a test project for chapter tests."""
    project_data = {
        "title": "Test Book for Chapters",
        "author": "Chapter Tester",
        "description": "A book to test chapter functionality",
    }
    response = client.post("/api/projects", json=project_data)
    return response.json()


class TestChapterCreate:
    """Test chapter creation endpoint."""

    def test_create_chapter_success(self, client, test_project):
        """Test successful chapter creation."""
        chapter_data = {
            "title": "Chapter 1: Introduction",
            "content": "This is the introduction content.",
            "position": 1,
        }

        response = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == chapter_data["title"]
        assert data["content"] == chapter_data["content"]
        assert data["position"] == chapter_data["position"]
        assert data["project_id"] == test_project["id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_chapter_minimal(self, client, test_project):
        """Test chapter creation with minimal data."""
        chapter_data = {
            "title": "Minimal Chapter",
        }

        response = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == chapter_data["title"]
        assert data["content"] == ""
        assert data["position"] == 1  # Auto-assigned

    def test_create_chapter_auto_position(self, client, test_project):
        """Test automatic position assignment for chapters."""
        # Create first chapter
        chapter1 = {
            "title": "Chapter 1",
            "content": "First chapter",
        }
        response1 = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter1
        )
        assert response1.json()["position"] == 1

        # Create second chapter without position
        chapter2 = {
            "title": "Chapter 2",
            "content": "Second chapter",
        }
        response2 = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter2
        )
        assert response2.json()["position"] == 2

    def test_create_chapter_nonexistent_project(self, client):
        """Test chapter creation for nonexistent project."""
        chapter_data = {
            "title": "Orphan Chapter",
            "content": "This should fail",
        }

        response = client.post("/api/projects/999999/chapters", json=chapter_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_chapter_validation_error(self, client, test_project):
        """Test chapter creation with invalid data."""
        # Empty title
        chapter_data = {
            "title": "",
            "content": "Content without title",
        }

        response = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter_data
        )

        assert response.status_code == 422


class TestChapterRead:
    """Test chapter reading endpoints."""

    def test_get_chapter_by_id(self, client, test_project):
        """Test getting a chapter by ID."""
        # Create a chapter first
        chapter_data = {
            "title": "Chapter to Retrieve",
            "content": "Some content",
        }
        create_response = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter_data
        )
        chapter_id = create_response.json()["id"]

        # Get the chapter
        response = client.get(
            f"/api/projects/{test_project['id']}/chapters/{chapter_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chapter_id
        assert data["title"] == chapter_data["title"]
        assert data["content"] == chapter_data["content"]
        assert data["project_id"] == test_project["id"]

    def test_get_nonexistent_chapter(self, client, test_project):
        """Test getting a chapter that doesn't exist."""
        response = client.get(f"/api/projects/{test_project['id']}/chapters/999999")

        assert response.status_code == 404
        assert "chapter not found" in response.json()["detail"].lower()

    def test_list_chapters(self, client, test_project):
        """Test listing all chapters for a project."""
        # Create multiple chapters
        chapters = [
            {"title": "Chapter 1", "content": "Content 1", "position": 1},
            {"title": "Chapter 2", "content": "Content 2", "position": 2},
            {"title": "Chapter 3", "content": "Content 3", "position": 3},
        ]

        for chapter in chapters:
            client.post(f"/api/projects/{test_project['id']}/chapters", json=chapter)

        # List all chapters
        response = client.get(f"/api/projects/{test_project['id']}/chapters")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be ordered by position
        assert data[0]["title"] == "Chapter 1"
        assert data[1]["title"] == "Chapter 2"
        assert data[2]["title"] == "Chapter 3"

    def test_list_chapters_empty(self, client, test_project):
        """Test listing chapters when none exist."""
        response = client.get(f"/api/projects/{test_project['id']}/chapters")

        assert response.status_code == 200
        assert response.json() == []


class TestChapterUpdate:
    """Test chapter update endpoint."""

    def test_update_chapter_content(self, client, test_project):
        """Test updating chapter content."""
        # Create a chapter
        chapter_data = {
            "title": "Original Title",
            "content": "Original content",
            "position": 1,
        }
        create_response = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter_data
        )
        chapter_id = create_response.json()["id"]

        # Update the chapter
        update_data = {
            "title": "Updated Title",
            "content": "Updated content with more details",
        }
        response = client.patch(
            f"/api/projects/{test_project['id']}/chapters/{chapter_id}",
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chapter_id
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["position"] == 1  # Unchanged

    def test_update_chapter_position(self, client, test_project):
        """Test updating chapter position (reordering)."""
        # Create multiple chapters
        chapters = [
            {"title": "Chapter 1", "position": 1},
            {"title": "Chapter 2", "position": 2},
            {"title": "Chapter 3", "position": 3},
        ]
        chapter_ids = []
        for chapter in chapters:
            response = client.post(
                f"/api/projects/{test_project['id']}/chapters", json=chapter
            )
            chapter_ids.append(response.json()["id"])

        # Move Chapter 3 to position 1
        update_data = {"position": 1}
        response = client.patch(
            f"/api/projects/{test_project['id']}/chapters/{chapter_ids[2]}",
            json=update_data,
        )

        assert response.status_code == 200

        # Verify new order
        list_response = client.get(f"/api/projects/{test_project['id']}/chapters")
        chapters_list = list_response.json()

        assert chapters_list[0]["title"] == "Chapter 3"
        assert chapters_list[0]["position"] == 1
        assert chapters_list[1]["position"] == 2
        assert chapters_list[2]["position"] == 3

    def test_update_nonexistent_chapter(self, client, test_project):
        """Test updating a chapter that doesn't exist."""
        update_data = {"title": "New Title"}
        response = client.patch(
            f"/api/projects/{test_project['id']}/chapters/999999", json=update_data
        )

        assert response.status_code == 404


class TestChapterDelete:
    """Test chapter deletion endpoint."""

    def test_delete_chapter(self, client, test_project):
        """Test deleting a chapter."""
        # Create a chapter
        chapter_data = {
            "title": "Chapter to Delete",
            "content": "This will be deleted",
        }
        create_response = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter_data
        )
        chapter_id = create_response.json()["id"]

        # Delete the chapter
        response = client.delete(
            f"/api/projects/{test_project['id']}/chapters/{chapter_id}"
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/projects/{test_project['id']}/chapters/{chapter_id}"
        )
        assert get_response.status_code == 404

    def test_delete_chapter_reorders_positions(self, client, test_project):
        """Test that deleting a chapter reorders remaining chapters."""
        # Create multiple chapters
        chapters = [
            {"title": "Chapter 1", "position": 1},
            {"title": "Chapter 2", "position": 2},
            {"title": "Chapter 3", "position": 3},
        ]
        chapter_ids = []
        for chapter in chapters:
            response = client.post(
                f"/api/projects/{test_project['id']}/chapters", json=chapter
            )
            chapter_ids.append(response.json()["id"])

        # Delete Chapter 2
        client.delete(f"/api/projects/{test_project['id']}/chapters/{chapter_ids[1]}")

        # Verify remaining chapters are reordered
        list_response = client.get(f"/api/projects/{test_project['id']}/chapters")
        remaining = list_response.json()

        assert len(remaining) == 2
        assert remaining[0]["title"] == "Chapter 1"
        assert remaining[0]["position"] == 1
        assert remaining[1]["title"] == "Chapter 3"
        assert remaining[1]["position"] == 2

    def test_delete_nonexistent_chapter(self, client, test_project):
        """Test deleting a chapter that doesn't exist."""
        response = client.delete(f"/api/projects/{test_project['id']}/chapters/999999")

        assert response.status_code == 404


class TestChapterImportExport:
    """Test chapter import/export functionality."""

    def test_export_chapter_markdown(self, client, test_project):
        """Test exporting a chapter as Markdown."""
        # Create a chapter with Markdown content
        chapter_data = {
            "title": "Chapter with Markdown",
            "content": "# Heading\n\nSome **bold** text and *italic* text.",
        }
        create_response = client.post(
            f"/api/projects/{test_project['id']}/chapters", json=chapter_data
        )
        chapter_id = create_response.json()["id"]

        # Export as Markdown
        response = client.get(
            f"/api/projects/{test_project['id']}/chapters/{chapter_id}/export"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        content = response.text
        assert "# Chapter with Markdown" in content
        assert "# Heading" in content
        assert "**bold**" in content

    def test_import_chapter_markdown(self, client, test_project):
        """Test importing a chapter from Markdown."""
        markdown_content = """# Imported Chapter

## Introduction

This chapter was imported from Markdown.

- Point 1
- Point 2
- Point 3

**Important:** This is a test.
"""

        response = client.post(
            f"/api/projects/{test_project['id']}/chapters/import",
            content=markdown_content,
            headers={"content-type": "text/markdown"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Imported Chapter"
        assert "## Introduction" in data["content"]
        assert "This chapter was imported" in data["content"]

    def test_bulk_export_chapters(self, client, test_project):
        """Test exporting all chapters as a single Markdown file."""
        # Create multiple chapters
        chapters = [
            {"title": "Chapter 1", "content": "Content of chapter 1"},
            {"title": "Chapter 2", "content": "Content of chapter 2"},
            {"title": "Chapter 3", "content": "Content of chapter 3"},
        ]
        for chapter in chapters:
            client.post(f"/api/projects/{test_project['id']}/chapters", json=chapter)

        # Export all chapters
        response = client.get(f"/api/projects/{test_project['id']}/chapters/export")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        content = response.text
        assert "# Chapter 1" in content
        assert "# Chapter 2" in content
        assert "# Chapter 3" in content
        assert "Content of chapter 1" in content

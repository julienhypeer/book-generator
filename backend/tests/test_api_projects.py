"""Tests for Project CRUD API endpoints."""

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
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


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


class TestProjectCreate:
    """Test project creation endpoint."""

    def test_create_project_success(self, client):
        """Test successful project creation."""
        project_data = {
            "title": "My Test Book",
            "author": "John Doe",
            "description": "A test book description",
        }

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == project_data["title"]
        assert data["author"] == project_data["author"]
        assert data["description"] == project_data["description"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_project_minimal(self, client):
        """Test project creation with minimal data."""
        project_data = {
            "title": "Minimal Book",
            "author": "Jane Doe",
        }

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == project_data["title"]
        assert data["author"] == project_data["author"]
        assert data["description"] is None

    def test_create_project_validation_error(self, client):
        """Test project creation with invalid data."""
        # Missing required fields
        project_data = {"title": "Missing Author"}

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == 422
        assert "author" in str(response.json())

    def test_create_project_empty_title(self, client):
        """Test project creation with empty title."""
        project_data = {
            "title": "",
            "author": "John Doe",
        }

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == 422


class TestProjectRead:
    """Test project reading endpoints."""

    def test_get_project_by_id(self, client):
        """Test getting a project by ID."""
        # Create a project first
        project_data = {
            "title": "Book to Retrieve",
            "author": "Test Author",
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Get the project
        response = client.get(f"/api/projects/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["title"] == project_data["title"]
        assert data["author"] == project_data["author"]

    def test_get_nonexistent_project(self, client):
        """Test getting a project that doesn't exist."""
        response = client.get("/api/projects/999999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_projects(self, client):
        """Test listing all projects."""
        # Create multiple projects
        projects = [
            {"title": "Book 1", "author": "Author 1"},
            {"title": "Book 2", "author": "Author 2"},
            {"title": "Book 3", "author": "Author 3"},
        ]

        for project in projects:
            client.post("/api/projects", json=project)

        # List all projects
        response = client.get("/api/projects")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        titles = [p["title"] for p in data]
        assert "Book 1" in titles
        assert "Book 2" in titles
        assert "Book 3" in titles

    def test_list_projects_empty(self, client):
        """Test listing projects when none exist."""
        response = client.get("/api/projects")

        assert response.status_code == 200
        assert response.json() == []


class TestProjectUpdate:
    """Test project update endpoint."""

    def test_update_project_metadata(self, client):
        """Test updating project metadata."""
        # Create a project
        project_data = {
            "title": "Original Title",
            "author": "Original Author",
            "description": "Original description",
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Update the project
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
        }
        response = client.patch(
            f"/api/projects/{project_id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["title"] == update_data["title"]
        assert data["author"] == project_data["author"]  # Unchanged
        assert data["description"] == update_data["description"]

    def test_update_nonexistent_project(self, client):
        """Test updating a project that doesn't exist."""
        update_data = {"title": "New Title"}
        response = client.patch("/api/projects/999999", json=update_data)

        assert response.status_code == 404

    def test_update_project_settings(self, client):
        """Test updating project settings JSON."""
        # Create a project
        project_data = {
            "title": "Book with Settings",
            "author": "Test Author",
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Update with settings
        update_data = {
            "settings": {
                "template": "academic",
                "font_size": "12pt",
                "line_height": 1.5,
            }
        }
        response = client.patch(
            f"/api/projects/{project_id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["settings"] == update_data["settings"]


class TestProjectDelete:
    """Test project deletion endpoint."""

    def test_delete_project(self, client):
        """Test deleting a project."""
        # Create a project
        project_data = {
            "title": "Book to Delete",
            "author": "Test Author",
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Delete the project
        response = client.delete(f"/api/projects/{project_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_project(self, client):
        """Test deleting a project that doesn't exist."""
        response = client.delete("/api/projects/999999")

        assert response.status_code == 404

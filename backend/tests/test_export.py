"""
Tests for PDF export functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import io
import PyPDF2

from app.main import app
from app.models.project import Project
from app.models.chapter import Chapter
from app.services.project_service import ProjectService
from app.services.chapter_service import ChapterService


class TestExportAPI:
    """Test suite for export endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_project(self, db_session: Session):
        """Create a sample project with chapters."""
        # Create project
        project_service = ProjectService(db_session)
        project = project_service.create({
            "title": "Test Book for Export",
            "author": "Test Author",
            "description": "A test book for PDF export"
        })
        
        # Create chapters
        chapter_service = ChapterService(db_session)
        
        chapter_service.create({
            "project_id": project.id,
            "title": "Chapter 1: Introduction",
            "content": """# Introduction

This is the **introduction** chapter with some *italic* text.

## Section 1.1

A list of items:
- Item 1
- Item 2
- Item 3

## Section 1.2

A table:

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
""",
            "position": 1
        })
        
        chapter_service.create({
            "project_id": project.id,
            "title": "Chapter 2: Main Content",
            "content": """# Main Content

This chapter contains the main content of the book.

> A blockquote with important information.

Some code:
```python
def hello_world():
    print("Hello, World!")
```

A footnote[^1].

[^1]: This is the footnote text.
""",
            "position": 2
        })
        
        chapter_service.create({
            "project_id": project.id,
            "title": "Chapter 3: Conclusion",
            "content": """# Conclusion

The final chapter with conclusions.

## Key Points

1. First point
2. Second point
3. Third point

---

*The End*
""",
            "position": 3
        })
        
        return project
    
    def test_export_pdf_success(self, client, sample_project):
        """Test successful PDF export."""
        response = client.post(f"/api/export/pdf/{sample_project.id}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers.get("content-disposition", "")
        
        # Verify it's a valid PDF
        pdf_content = io.BytesIO(response.content)
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_content)
            assert len(pdf_reader.pages) > 0
        except Exception:
            pytest.fail("Generated content is not a valid PDF")
    
    def test_export_pdf_with_config(self, client, sample_project):
        """Test PDF export with custom configuration."""
        config = {
            "page_format": "A4",
            "font_size": 12,
            "line_height": 1.8,
            "include_toc": True,
            "language": "fr"
        }
        
        response = client.post(
            f"/api/export/pdf/{sample_project.id}",
            json=config
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    
    def test_export_pdf_no_chapters(self, client, db_session):
        """Test PDF export with no chapters."""
        # Create empty project
        project_service = ProjectService(db_session)
        project = project_service.create({
            "title": "Empty Book",
            "author": "Test Author"
        })
        
        response = client.post(f"/api/export/pdf/{project.id}")
        
        assert response.status_code == 400
        assert "No chapters" in response.json()["detail"]
    
    def test_export_pdf_project_not_found(self, client):
        """Test PDF export with non-existent project."""
        response = client.post("/api/export/pdf/non-existent-id")
        
        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]
    
    def test_preview_export_html(self, client, sample_project):
        """Test HTML preview of export."""
        response = client.get(
            f"/api/export/preview/{sample_project.id}?format=html"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "project" in data
        assert data["project"]["id"] == sample_project.id
        assert data["project"]["title"] == sample_project.title
        
        assert "chapters" in data
        assert len(data["chapters"]) == 3
        
        # Check first chapter
        chapter = data["chapters"][0]
        assert chapter["title"] == "Chapter 1: Introduction"
        assert "<h1>" in chapter["html"] or "<h2>" in chapter["html"]
        assert "<strong>introduction</strong>" in chapter["html"]
        
        assert "css" in data
        assert len(data["css"]) > 0
    
    def test_preview_export_no_chapters(self, client, db_session):
        """Test preview with no chapters."""
        # Create empty project
        project_service = ProjectService(db_session)
        project = project_service.create({
            "title": "Empty Book",
            "author": "Test Author"
        })
        
        response = client.get(f"/api/export/preview/{project.id}")
        
        assert response.status_code == 400
        assert "No chapters" in response.json()["detail"]
    
    def test_export_with_french_typography(self, client, db_session):
        """Test export with French typography."""
        # Create project with French content
        project_service = ProjectService(db_session)
        project = project_service.create({
            "title": "Livre en Français",
            "author": "Auteur Test"
        })
        
        chapter_service = ChapterService(db_session)
        chapter_service.create({
            "project_id": project.id,
            "title": "Chapitre 1",
            "content": """# Introduction

"Les guillemets français" sont utilisés ici.

Voici une liste :
- Premier élément
- Deuxième élément

Un texte avec des espaces insécables avant les signes de ponctuation !
""",
            "position": 1
        })
        
        response = client.get(f"/api/export/preview/{project.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        html = data["chapters"][0]["html"]
        # Check for French typography
        assert "«" in html or "guillemets" in html
    
    def test_export_with_math(self, client, db_session):
        """Test export with math content."""
        # Create project with math
        project_service = ProjectService(db_session)
        project = project_service.create({
            "title": "Math Book",
            "author": "Test Author"
        })
        
        chapter_service = ChapterService(db_session)
        chapter_service.create({
            "project_id": project.id,
            "title": "Math Chapter",
            "content": """# Mathematics

Inline math: $E = mc^2$

Display math:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$
""",
            "position": 1
        })
        
        config = {"enable_math": True}
        
        response = client.post(
            f"/api/export/pdf/{project.id}",
            json=config
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
"""
Tests for template API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestTemplatesAPI:
    """Test suite for templates API."""

    def test_list_templates(self, client):
        """Test listing available templates."""
        response = client.get("/api/templates/list")
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        assert "book" in templates
        assert "academic" in templates
        assert "novel" in templates

    def test_generate_css_default(self, client):
        """Test generating CSS with default settings."""
        response = client.post(
            "/api/templates/generate",
            json={"template_name": "book"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "css" in data
        assert data["template_name"] == "book"
        assert "@page" in data["css"]

    def test_generate_css_custom_settings(self, client):
        """Test generating CSS with custom settings."""
        response = client.post(
            "/api/templates/generate",
            json={
                "template_name": "academic",
                "page_settings": {
                    "format": "A4",
                    "margins": {"top": 25, "bottom": 25, "left": 30, "right": 20},
                },
                "typography": {
                    "font_family": "Times New Roman, serif",
                    "font_size": "12pt",
                    "line_height": 2.0,
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "Times New Roman" in data["css"]
        assert "A4" in data["css"] or "210mm 297mm" in data["css"]

    def test_generate_css_minified(self, client):
        """Test generating minified CSS."""
        response = client.post(
            "/api/templates/generate",
            json={
                "template_name": "book",
                "minify": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["minified"] is True
        # Minified CSS should not have multiple spaces
        assert "  " not in data["css"]

    def test_generate_css_invalid_template(self, client):
        """Test generating CSS with invalid template."""
        response = client.post(
            "/api/templates/generate",
            json={"template_name": "invalid_template"},
        )
        assert response.status_code == 400

    def test_preview_template(self, client):
        """Test template preview generation."""
        response = client.post(
            "/api/templates/preview",
            json={
                "template_name": "book",
                "sample_content": "<h1>Test Chapter</h1><p>Test content</p>",
            },
        )
        assert response.status_code == 200
        html = response.text
        assert "<html" in html
        assert "<style>" in html
        assert "Test Chapter" in html

    def test_get_template_css(self, client):
        """Test getting CSS for specific template."""
        response = client.get("/api/templates/book/css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
        css = response.text
        assert "@page" in css

    def test_get_template_css_minified(self, client):
        """Test getting minified CSS."""
        response = client.get("/api/templates/book/css?minify=true")
        assert response.status_code == 200
        css = response.text
        # Minified CSS characteristics
        assert "\n\n" not in css  # No double newlines

    def test_get_template_css_invalid(self, client):
        """Test getting CSS for invalid template."""
        response = client.get("/api/templates/invalid/css")
        assert response.status_code == 404

    def test_get_template_presets(self, client):
        """Test getting template presets."""
        response = client.get("/api/templates/presets")
        assert response.status_code == 200
        presets = response.json()
        assert "book" in presets
        assert "academic" in presets
        assert "novel" in presets

        # Check preset structure
        book_preset = presets["book"]
        assert "description" in book_preset
        assert "page_format" in book_preset
        assert "font" in book_preset
        assert "suitable_for" in book_preset

    def test_validate_template_config(self, client):
        """Test template configuration validation."""
        # Valid config
        response = client.post(
            "/api/templates/validate",
            json={
                "template_name": "book",
                "page_settings": {
                    "format": "156mm 234mm",
                    "margins": {"top": 20, "bottom": 20, "left": 15, "right": 15},
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert len(data["errors"]) == 0

        # Invalid template name
        response = client.post(
            "/api/templates/validate",
            json={"template_name": "invalid"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_template_with_warnings(self, client):
        """Test validation with warnings."""
        response = client.post(
            "/api/templates/validate",
            json={
                "template_name": "book",
                "page_settings": {
                    "format": "A4",
                    "margins": {"top": 150, "bottom": 20, "left": 15, "right": 15},
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True  # Still valid
        assert len(data["warnings"]) > 0  # But has warnings

    def test_clear_template_cache(self, client):
        """Test clearing template cache."""
        response = client.delete("/api/templates/cache")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_french_typography(self, client):
        """Test French typography settings."""
        response = client.post(
            "/api/templates/generate",
            json={
                "template_name": "book",
                "typography": {
                    "language": "fr",
                    "quotes_style": "french",
                    "spacing_rules": "french",
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        css = data["css"]
        # Check for French quotes
        assert "«" in css and "»" in css

    def test_custom_css_integration(self, client):
        """Test custom CSS integration."""
        custom_css = """
        .custom-class {
            color: red;
            font-weight: bold;
        }
        """
        response = client.post(
            "/api/templates/generate",
            json={
                "template_name": "book",
                "custom_css": custom_css,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert ".custom-class" in data["css"]
        assert "color: red" in data["css"]

    def test_special_pages_settings(self, client):
        """Test special pages configuration."""
        response = client.post(
            "/api/templates/generate",
            json={
                "template_name": "book",
                "special_pages": {
                    "title_page": {"text_align": "center", "margin_top": "30%"},
                    "copyright_page": {"font_size": "0.9em"},
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert ".title-page" in data["css"]
        assert ".copyright-page" in data["css"]

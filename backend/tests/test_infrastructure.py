"""Tests for infrastructure setup and configuration."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.database import init_database, get_db
from app.core.config import Settings


class TestDatabaseSetup:
    """Test database initialization and configuration."""

    def test_database_creation(self, tmp_path):
        """Test that database file is created with correct structure."""
        db_path = tmp_path / "test.db"
        settings = Settings(database_url=f"sqlite:///{db_path}")

        engine = init_database(settings)

        assert db_path.exists()
        assert db_path.stat().st_size > 0

        # Verify tables are created
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "projects" in tables
        assert "chapters" in tables

    def test_database_models_structure(self, tmp_path):
        """Test that database models have correct columns."""
        db_path = tmp_path / "test.db"
        settings = Settings(database_url=f"sqlite:///{db_path}")

        engine = init_database(settings)
        inspector = inspect(engine)

        # Check projects table structure
        project_columns = {
            col["name"] for col in inspector.get_columns("projects")
        }
        expected_project_cols = {
            "id",
            "title",
            "author",
            "description",
            "created_at",
            "updated_at",
            "settings_json",
        }
        assert expected_project_cols.issubset(project_columns)

        # Check chapters table structure
        chapter_columns = {
            col["name"] for col in inspector.get_columns("chapters")
        }
        expected_chapter_cols = {
            "id",
            "project_id",
            "title",
            "content",
            "position",
            "created_at",
            "updated_at",
        }
        assert expected_chapter_cols.issubset(chapter_columns)

    def test_database_session_creation(self, tmp_path):
        """Test that database sessions work correctly."""
        db_path = tmp_path / "test.db"
        settings = Settings(database_url=f"sqlite:///{db_path}")

        engine = init_database(settings)

        # Test session creation
        db_gen = get_db(engine)
        session = next(db_gen)

        assert isinstance(session, Session)
        assert session.is_active

        # Cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass

    def test_database_foreign_keys_enabled(self, tmp_path):
        """Test that foreign keys are enabled in SQLite."""
        from sqlalchemy import text

        db_path = tmp_path / "test.db"
        settings = Settings(database_url=f"sqlite:///{db_path}")

        engine = init_database(settings)

        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys"))
            fk_status = result.fetchone()[0]

        assert fk_status == 1  # Foreign keys should be enabled


class TestWeasyPrintSetup:
    """Test WeasyPrint configuration."""

    def test_weasyprint_import(self):
        """Test that WeasyPrint is installed and importable."""
        try:
            import weasyprint

            assert hasattr(weasyprint, "HTML")
            assert hasattr(weasyprint, "CSS")
        except ImportError:
            pytest.fail("WeasyPrint is not installed")

    def test_weasyprint_configuration(self):
        """Test WeasyPrint configuration for book format."""
        from app.core.pdf_config import get_weasyprint_config

        config = get_weasyprint_config()

        assert config["page_width"] == "156mm"
        assert config["page_height"] == "234mm"
        assert config["margin_top"] == "20mm"
        assert config["margin_bottom"] == "20mm"
        assert config["margin_left"] == "15mm"
        assert config["margin_right"] == "15mm"
        assert config["font_size"] == "11pt"
        assert config["line_height"] == "1.6"

    def test_weasyprint_css_generation(self):
        """Test generation of CSS for print media."""
        from app.core.pdf_config import generate_print_css

        css = generate_print_css()

        # Check for essential CSS rules
        assert "@page" in css
        assert "size: 156mm 234mm" in css
        assert "@bottom-center" in css
        assert "counter(page)" in css
        assert "hyphens: auto" in css
        assert 'hyphenate-language: "fr"' in css

    def test_weasyprint_pdf_generation(self, tmp_path):
        """Test basic PDF generation with WeasyPrint."""
        from app.core.pdf_config import (
            generate_test_pdf,
            is_weasyprint_available,
        )

        # Skip test if WeasyPrint is not available
        if not is_weasyprint_available():
            pytest.skip("WeasyPrint not installed")

        output_path = tmp_path / "test.pdf"
        html_content = "<h1>Test Book</h1><p>Test content</p>"

        result = generate_test_pdf(html_content, str(output_path))

        assert result is True
        assert output_path.exists()
        # PDF should have some content
        assert output_path.stat().st_size > 1000

    def test_weasyprint_availability_check(self):
        """Test WeasyPrint availability check function."""
        from app.core.pdf_config import is_weasyprint_available

        # This should be True in our test environment
        # but the function should exist and return a boolean
        result = is_weasyprint_available()
        assert isinstance(result, bool)


class TestStorageSetup:
    """Test storage directory structure initialization."""

    def test_storage_directories_creation(self, tmp_path):
        """Test that all required storage directories are created."""
        from app.core.storage import init_storage

        storage_root = tmp_path / "storage"
        settings = Settings(storage_path=str(storage_root))

        init_storage(settings)

        # Check all required directories exist
        assert (storage_root / "projects").exists()
        assert (storage_root / "templates").exists()
        assert (storage_root / "exports").exists()
        assert (storage_root / "temp").exists()

    def test_storage_permissions(self, tmp_path):
        """Test that storage directories have correct permissions."""
        from app.core.storage import init_storage

        storage_root = tmp_path / "storage"
        settings = Settings(storage_path=str(storage_root))

        init_storage(settings)

        # Check directories are writable
        test_file = storage_root / "projects" / "test.txt"
        test_file.write_text("test")
        assert test_file.read_text() == "test"
        test_file.unlink()

    def test_storage_cleanup_temp(self, tmp_path):
        """Test that temp directory is cleaned on init."""
        from app.core.storage import init_storage

        storage_root = tmp_path / "storage"
        temp_dir = storage_root / "temp"
        temp_dir.mkdir(parents=True)

        # Create old temp file
        old_file = temp_dir / "old_temp.txt"
        old_file.write_text("old content")

        settings = Settings(storage_path=str(storage_root))
        init_storage(settings)

        # Old temp files should be removed
        assert not old_file.exists()
        assert temp_dir.exists()  # But directory should still exist

    def test_default_templates_copy(self, tmp_path):
        """Test that default templates are copied on first init."""
        from app.core.storage import init_storage

        storage_root = tmp_path / "storage"
        settings = Settings(storage_path=str(storage_root))

        init_storage(settings)

        templates_dir = storage_root / "templates"

        # Check default templates exist
        assert (templates_dir / "roman.css").exists()
        assert (templates_dir / "technical.css").exists()
        assert (templates_dir / "academic.css").exists()

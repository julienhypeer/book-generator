# Changelog

## [Unreleased]

### Added
- Initial project setup with backend infrastructure
- SQLite database configuration with foreign keys support
- WeasyPrint configuration for professional book PDF generation (156mm x 234mm format)
- Project and Chapter models with SQLAlchemy ORM
- Complete CRUD API for Projects management
- Pydantic schemas for request/response validation
- Service layer architecture with ProjectService
- 26 unit tests with TDD approach
- 3 CSS templates (roman, technical, academic)
- Docker configuration for development and production
- FastAPI application with lifecycle management

### Technical Details
- Python 3.11 with FastAPI framework
- SQLite database (with PostgreSQL migration path planned)
- WeasyPrint for PDF generation
- Black for code formatting
- Flake8 for linting
- Pytest for testing
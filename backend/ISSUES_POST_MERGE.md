# Issues à créer après merge de PR #1

## Issue #1: Migrer vers PostgreSQL pour production
**Title**: Migrate from SQLite to PostgreSQL for production
**Labels**: enhancement, backend, database
**Description**:
```markdown
## Context
SQLite is currently used for development but has limitations for production:
- Single writer limitation
- No concurrent writes
- Limited performance for multiple users

## Acceptance Criteria
- [ ] Add PostgreSQL support alongside SQLite
- [ ] Create migration scripts from SQLite to PostgreSQL
- [ ] Update docker-compose with PostgreSQL service
- [ ] Add connection pooling configuration
- [ ] Update documentation

## Technical Details
- Use SQLAlchemy's database agnostic approach
- Support both databases via DATABASE_URL environment variable
- Add alembic for database migrations
- Test with pgbouncer for connection pooling

## References
- Current implementation: `/backend/app/core/database.py`
```

## Issue #2: Embed fonts locally instead of system dependencies
**Title**: Embed fonts locally to avoid system dependencies
**Labels**: enhancement, backend, pdf
**Description**:
```markdown
## Context
Currently requires system font installation which complicates deployment:
```bash
apt-get install fonts-liberation fonts-dejavu-core
```

## Acceptance Criteria
- [ ] Bundle required fonts in the project
- [ ] Configure WeasyPrint to use local fonts
- [ ] Remove system font dependencies
- [ ] Test on clean Docker container
- [ ] Update documentation

## Technical Details
- Add fonts directory in `/backend/fonts/`
- Configure font paths in WeasyPrint
- Include fonts in Docker image
- Test with common fonts: Liberation, DejaVu, Noto

## References
- Current implementation: `/backend/app/core/pdf_config.py`
- WeasyPrint docs: https://doc.courtbouillon.org/weasyprint/stable/api_reference.html#fonts
```

## Issue #3: Add memory limits for WeasyPrint processes
**Title**: Implement memory limits for WeasyPrint PDF generation
**Labels**: enhancement, backend, performance, security
**Description**:
```markdown
## Context
WeasyPrint can consume significant memory for large documents (2GB+ for 1000 pages).
Need to implement memory limits to prevent OOM errors.

## Acceptance Criteria
- [ ] Implement memory limits per PDF generation process
- [ ] Add graceful error handling when limits are reached
- [ ] Implement document chunking for large PDFs
- [ ] Add monitoring/metrics for memory usage
- [ ] Configure limits via environment variables

## Technical Details
```python
# Current placeholder in CLAUDE.md:
import resource
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, -1))  # 2GB max
```

- Implement process isolation with multiprocessing
- Add memory monitoring with psutil
- Chunk large documents (>100 pages) and merge PDFs
- Add Prometheus metrics for monitoring

## References
- Memory management suggestion: `/backend/CLAUDE.md`
- WeasyPrint optimization: https://doc.courtbouillon.org/weasyprint/stable/tips_tricks.html
```

## Issue #4: Version CSS templates for better maintainability
**Title**: Implement versioning system for CSS templates
**Labels**: enhancement, backend, frontend
**Description**:
```markdown
## Context
CSS templates are currently static files. Need versioning for:
- Template updates without breaking existing projects
- A/B testing different styles
- Custom template management

## Acceptance Criteria
- [ ] Implement template versioning system
- [ ] Add migration path for template updates
- [ ] Create template marketplace/gallery UI
- [ ] Add custom template upload capability
- [ ] Implement template inheritance/extends

## Technical Details
- Store template versions in database
- Create template model with version field
- Implement template migration scripts
- Add template preview generation
- Support SCSS compilation for advanced templates

## Database Schema
```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    version VARCHAR(50),
    css_content TEXT,
    parent_template_id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## References
- Current templates: `/backend/app/core/storage.py`
- Template files: `/backend/storage/templates/`
```

## How to create these issues:

1. After PR #1 is merged
2. Go to GitHub Issues
3. Create each issue with the provided title, labels, and description
4. Add to project board if applicable
5. Assign priorities based on impact:
   - High: Issue #1 (PostgreSQL) and #3 (Memory limits)
   - Medium: Issue #2 (Fonts)
   - Low: Issue #4 (Template versioning)
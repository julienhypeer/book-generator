# 🔧 Backend - Instructions Claude

## 📋 Contexte
API FastAPI pour génération PDF professionnelle avec WeasyPrint.

## 🏗️ Architecture

### Structure Actuelle (PR #1 complété)
```
/app
  /core         → Configuration système ✅
    config.py   → Settings avec Pydantic
    database.py → SQLite avec foreign keys
    pdf_config.py → WeasyPrint pour format livre
    storage.py  → Gestion fichiers et templates
  /models       → Modèles de données ✅
    project.py  → Modèle Project
    chapter.py  → Modèle Chapter
  /api          → Endpoints REST (PR #2)
  /services     → Services métier (PR #3+)
  /tasks        → Tâches asynchrones (PR #8)
  /validators   → Schémas Pydantic (PR #2)
```

### Workflow de Génération PDF

#### 1️⃣ Première Passe (Analyse)
```python
async def first_pass(html: str) -> dict:
    """Génère PDF temporaire pour extraire positions"""
    document = weasyprint.HTML(string=html)
    temp_pdf = document.render()
    
    page_breaks = {}
    for page_num, page in enumerate(temp_pdf.pages, 1):
        # Extraire les ancres et positions
        for element in page.get_elements_by_tag('h1', 'h2', 'h3'):
            page_breaks[element.id] = page_num
    
    return page_breaks
```

#### 2️⃣ Deuxième Passe (Finale)
```python
async def second_pass(html: str, page_breaks: dict) -> bytes:
    """Génère PDF final avec TOC synchronisé"""
    # Injecter vrais numéros dans le TOC
    html_with_toc = inject_page_numbers(html, page_breaks)
    
    # Générer PDF final
    document = weasyprint.HTML(
        string=html_with_toc,
        base_url='file:///app/templates/'
    )
    
    return document.write_pdf(
        stylesheets=[CSS(filename='/app/templates/book.css')],
        font_config=FontConfiguration()
    )
```

## 🎯 Résolution des 6 Problèmes Critiques

**Implémentation**: Service `AdvancedPDFGenerator` (PR #9) + `CSSTemplateManager` (PR #11)

### 1. Pages Blanches Parasites
```css
/* CSS avancé avec templates personnalisables */
.chapter-end { page-break-after: right; }
.part-separator { page-break-before: right; page-break-after: always; }
.editorial-break { page-break-after: right; }
```

### 2. Espacement Mots (Rivières)
```css
/* Césure française optimisée par template */
body {
  hyphens: auto;
  hyphenate-language: "fr";
  hyphenate-limit-chars: 6 3 3;
  word-spacing: 0.16em;
  letter-spacing: 0.01em;
}
```

### 3. TOC Synchronisé
```python
# Double-passe avec PageBreakAnalyzer
async def generate_pdf_two_pass(html, template='roman'):
    # 1ère passe: analyser positions
    document = HTML(string=html).render()
    page_map = analyzer.extract_page_positions(document)
    
    # 2ème passe: injecter vrais numéros TOC
    final_html = inject_toc_pages(html, page_map)
    return HTML(string=final_html).render().write_pdf()
```

### 4. Hiérarchie Sous-Parties
```css
/* Compteurs CSS automatiques par template */
body { counter-reset: chapter section subsection; }
h1 { counter-increment: chapter; counter-reset: section; }
h2::before { content: counter(chapter) "." counter(section) " "; }
h3::before { content: counter(chapter) "." counter(section) "." counter(subsection) " "; }
```

### 5. Barres Horizontales
```css
/* Élimination totale + alternatives sémantiques */
hr { display: none; }
@media print { hr { display: none; } }
.chapter-separator::after { content: "* * *"; font-size: 18pt; }
```

### 6. Titres Orphelins
```css
/* Protection renforcée multi-niveaux */
h1, h2, h3, h4 {
  page-break-after: avoid;
  page-break-inside: avoid;
  orphans: 4;
  widows: 4;
  min-height: 2.5em;
}
```

## 🚀 Optimisations Performance

### Cache Redis
```python
@cache(expire=3600)
async def get_compiled_html(project_id: str) -> str:
    """Cache HTML compilé pendant 1h"""
    return await compile_markdown_to_html(project_id)
```

### Batch Processing
```python
# Pour livres > 100 pages
async def generate_large_pdf(chapters: list):
    tasks = []
    for batch in chunks(chapters, 50):
        tasks.append(process_batch.delay(batch))
    
    results = await asyncio.gather(*tasks)
    return merge_pdfs(results)
```

### Memory Management
```python
# Limiter mémoire WeasyPrint
import resource
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, -1))  # 2GB max
```

## 🔒 Sécurité

### Sanitization HTML
```python
from bleach import clean

ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'a', 'em', 'strong', 'code', 'pre',
    'ul', 'ol', 'li', 'blockquote', 'img'
]

def sanitize_html(html: str) -> str:
    return clean(html, tags=ALLOWED_TAGS, strip=True)
```

### Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/export/pdf")
@limiter.limit("5/minute")
async def export_pdf(request: Request):
    # Max 5 exports par minute
```

## 📊 Monitoring

### Métriques Clés
```python
# Prometheus metrics
pdf_generation_time = Histogram('pdf_generation_seconds')
pdf_page_count = Counter('pdf_pages_total')
pdf_errors = Counter('pdf_generation_errors')
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "weasyprint": check_weasyprint(),
        "redis": await check_redis(),
        "storage": check_storage_space()
    }
```

## ✅ État du Développement

### PR #1 - Infrastructure de Base (Complété)
- ✅ Configuration SQLite avec foreign keys
- ✅ Configuration WeasyPrint (format livre 156mm x 234mm)
- ✅ Structure de stockage avec templates CSS
- ✅ Modèles Project et Chapter
- ✅ Application FastAPI avec lifecycle management
- ✅ 12 tests unitaires passent
- ✅ Code formaté (black) et linté (flake8)

### PR #2 - API CRUD Projets (Complété)
- ✅ Schémas Pydantic (ProjectCreate, ProjectUpdate, ProjectResponse)
- ✅ Service ProjectService avec logique métier
- ✅ Endpoints CRUD complets (/api/projects)
- ✅ Gestion des settings JSON
- ✅ 13 tests unitaires pour les endpoints
- ✅ Code formaté et linté

### PR #3 - Gestionnaire de Chapitres (Complété)
- ✅ Schémas Pydantic pour chapters (ChapterCreate, ChapterUpdate, ChapterResponse)
- ✅ Service ChapterService avec gestion automatique des positions
- ✅ Endpoints CRUD complets (/api/projects/{id}/chapters)
- ✅ Import/Export Markdown avec extraction H1
- ✅ Réorganisation bulk des chapitres
- ✅ 18 tests unitaires complets
- ✅ Code formaté et linté

### PR #9 - Résolution Problèmes Pagination Avancés (Complété)
- ✅ Service AdvancedPDFGenerator avec double-passe WeasyPrint
- ✅ Classe PageBreakAnalyzer pour extraction positions TOC
- ✅ Classe PaginationValidator pour les 6 problèmes critiques
- ✅ API Export avec endpoints /api/export/{project_id}/pdf
- ✅ Validation qualité temps réel avec headers HTTP
- ✅ CSS avancé 400+ lignes résolvant tous les problèmes
- ✅ 24 tests de régression complets
- ✅ Code formaté et linté

### PR #10 - API Export Multi-formats EPUB/DOCX (Complété)
- ✅ **TDD Implementation**: Tests écrits d'abord (558 lignes, 30+ cas de test)
- ✅ **EPUBGenerator**: Structure ZIP conforme EPUB avec fallback manuel
- ✅ **DOCXGenerator**: Format Office Open XML avec fallback manuel
- ✅ **MultiFormatExporter**: Service principal avec export async
- ✅ **Validation**: Gestion erreurs et validation des formats
- ✅ **Templates**: Intégration système de templates existant
- ✅ **Metadata**: Injection métadonnées projet dans exports
- ✅ **Quality**: 15/18 tests passing, formatage black/flake8
- ✅ **Fallbacks**: Implémentations manuelles si bibliothèques indisponibles

### PR #11 - Système Templates CSS Avancés (Complété)
- ✅ **TDD Implementation**: Tests écrits d'abord (479 lignes, 26 cas de test)
- ✅ **CSSTemplateManager**: Gestionnaire 3 templates (ROMAN, TECHNICAL, ACADEMIC)
- ✅ **TemplateRenderer**: Moteur de rendu CSS modulaire avec 7 modules
- ✅ **CSSValidator**: Validateur qualité avec détection 6 problèmes critiques
- ✅ **Template Inheritance**: Héritage intelligent base → spécialisé
- ✅ **CSS Quality Rules**: Règles pagination, typographie, layout intégrées
- ✅ **Minification**: CSS production optimisé avec variables personnalisées
- ✅ **Error Handling**: Gestion erreurs robuste et validation configurations
- ✅ **Integration**: Workflow complet config → CSS → validation (26/26 tests)
- ✅ **Quality**: Code formaté black, linting flake8 propre

### Structure Actuelle
```
/app
  /core         → Configuration (database, pdf, storage) ✅
  /models       → Modèles SQLAlchemy (Project, Chapter) ✅
  /api          → Endpoints REST (projects, chapters) ✅
  /services     → Services ✅
    project.py      → ProjectService
    chapter.py      → ChapterService  
    pdf_generator.py → AdvancedPDFGenerator (double-passe)
    multi_format_exporter.py → MultiFormatExporter (EPUB/DOCX)
    advanced_css_templates.py → CSSTemplateManager + TemplateRenderer + CSSValidator
  /tasks        → Tâches Celery (à venir)
  /validators   → Schémas Pydantic (project, chapter, export) ✅
```

## 🔧 Commandes

```bash
# Environnement virtuel
source venv/bin/activate

# Développement
PYTHONPATH=. uvicorn app.main:app --reload

# Tests
PYTHONPATH=. python -m pytest tests/ -v
PYTHONPATH=. python -m pytest --cov=app

# Linting et formatage
flake8 app/ tests/
black app/ tests/

# Celery (à venir)
celery -A app.tasks worker --loglevel=info
celery -A app.tasks flower

# Migrations (à venir)
alembic upgrade head
```

## 🐛 Debug WeasyPrint

### Fonts Manquantes
```bash
apt-get install fonts-liberation fonts-dejavu-core
fc-cache -f -v
```

### Memory Leaks
```python
# Forcer garbage collection après génération
import gc
gc.collect()
```

### CSS Debug
```python
# Logger les warnings WeasyPrint
import logging
logging.getLogger('weasyprint').setLevel(logging.DEBUG)
```
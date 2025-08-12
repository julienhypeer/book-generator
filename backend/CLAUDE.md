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

### 1. Pages Blanches Parasites
```python
# Forcer pages blanches UNIQUEMENT éditoriales
CSS_RULES = """
.chapter-end { page-break-after: right; }
.part-separator { page-break-before: right; }
"""
```

### 2. Espacement Mots (Rivières)
```python
# Configuration césure française
HYPHENATION_CONFIG = {
    'language': 'fr',
    'min_chars': 5,
    'min_left': 3,
    'min_right': 2
}
```

### 3. TOC Synchronisé
```python
# Double passe obligatoire
def generate_pdf(content):
    page_map = first_pass(content)
    return second_pass(content, page_map)
```

### 4. Hiérarchie Sous-Parties
```css
/* CSS avec compteurs */
h2 { counter-increment: section; }
h3 { counter-increment: subsection; }
h2:before { content: counter(chapter) "." counter(section); }
```

### 5. Barres Horizontales
```css
/* Éviter artifacts Chrome */
hr { display: none; }
.chapter-separator { 
  border: none;
  margin: 2em 0;
}
```

### 6. Titres Orphelins
```css
h1, h2, h3, h4 {
  page-break-after: avoid;
  page-break-inside: avoid;
  orphans: 3;
  widows: 3;
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

### Structure Actuelle
```
/app
  /core         → Configuration (database, pdf, storage) ✅
  /models       → Modèles SQLAlchemy (Project, Chapter) ✅
  /api          → Endpoints REST (projects) ✅
  /services     → Services (ProjectService) ✅
  /tasks        → Tâches Celery (à venir - PR #8)
  /validators   → Schémas Pydantic (project) ✅
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
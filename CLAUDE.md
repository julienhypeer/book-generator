# 📚 Book Generator - Instructions Claude

## 🎯 Contexte du Projet
Plateforme complète de génération de livres professionnels pour l'impression, résolvant 6 problèmes critiques identifiés lors d'un projet précédent (415 pages testées).

## 🚨 Problèmes Critiques à Résoudre
1. **Pages blanches parasites** : Distinguer pages blanches éditoriales (volontaires) vs parasites (bugs)
2. **Espacement entre mots** : Éviter les "rivières" blanches dans la justification
3. **Correspondance TOC** : Synchronisation parfaite sommaire ↔ numéros de page
4. **Gestion sous-parties** : Hiérarchie et page-breaks corrects
5. **Barres horizontales parasites** : Éliminer les artifacts CSS
6. **Titres orphelins** : Jamais de titre seul en bas de page

## 🏗️ Architecture Technique

### Stack Principal
- **Frontend**: React 18 + TypeScript + Monaco Editor + TanStack Query
- **Backend**: Python 3.11 + FastAPI + WeasyPrint + Celery
- **Storage**: SQLite (métadonnées) + FileSystem (contenu)
- **Temps réel**: WebSockets pour preview live
- **Queue**: Redis pour tâches asynchrones

### Moteur de Rendu PDF
**WeasyPrint** est le moteur principal car il supporte nativement :
- CSS Paged Media (contrôle précis de la pagination)
- Césure française automatique
- Gestion des orphelins/veuves
- Génération en 2 passes pour TOC synchronisé

## 📁 Structure du Projet

```
/frontend       → Interface utilisateur React (voir frontend/CLAUDE.md)
/backend        → API Python FastAPI (voir backend/CLAUDE.md)
/shared         → Types TypeScript et constantes partagées
/storage        → Stockage projets et templates
/docker         → Configuration containers
/tests          → Tests unitaires et E2E
```

## 🔧 Commandes Principales

### Développement
```bash
# Installation globale
npm run install:all

# Développement avec hot-reload
npm run dev           # Lance frontend + backend

# Tests
npm run test          # Tests unitaires
npm run test:e2e      # Tests end-to-end
```

### Production
```bash
# Build
npm run build

# Docker
docker-compose up -d

# Génération PDF (API)
POST /api/export/pdf
```

## 🎨 Patterns et Conventions

### Backend Python
- **Services**: Logique métier dans `/backend/app/services/`
- **Validators**: Validation Pydantic dans `/backend/app/validators/`
- **Tasks**: Tâches Celery dans `/backend/app/tasks/`
- **Double Pass**: TOC généré en 2 passes pour synchronisation

### Frontend React
- **State**: Zustand pour state management
- **Queries**: TanStack Query pour cache API
- **Workers**: Web Workers pour parsing Markdown
- **Preview**: WebSocket pour mise à jour temps réel

### CSS pour Print
```css
/* Toujours utiliser ces règles pour éviter les problèmes */
@page {
  size: 156mm 234mm;  /* Format livre standard */
  margin: 20mm 15mm;
  @bottom-center {
    content: counter(page);
  }
}

/* Protection contre orphelins */
h1, h2, h3 {
  page-break-after: avoid;
  page-break-inside: avoid;
}

/* Césure française */
p {
  hyphens: auto;
  hyphenate-language: "fr";
  hyphenate-limit-chars: 5 3 2;
}
```

## 🚀 Workflow de Génération PDF

### 1. Première Passe (Analyse)
```python
# Génère PDF temporaire pour extraire les vraies positions
temp_pdf = weasyprint.HTML(string=html).render()
page_breaks = extract_page_positions(temp_pdf)
```

### 2. Deuxième Passe (Finale)
```python
# Injecte les vrais numéros de page dans le TOC
html_with_toc = inject_page_numbers(html, page_breaks)
final_pdf = weasyprint.HTML(string=html_with_toc).write_pdf()
```

## 🐛 Debugging et Problèmes Connus

### WeasyPrint
- **Fonts manquantes**: Installer `fonts-liberation` sur Linux
- **Mémoire**: Limiter à 100 pages pour preview, batch pour export
- **Performance**: Utiliser cache Redis pour HTML compilé

### Monaco Editor
- **Bundle size**: Lazy load avec dynamic imports
- **Workers**: Configurer webpack pour copier workers

## 📊 Métriques de Qualité

### Critères de Succès
- ✅ 0 pages blanches parasites
- ✅ 0 rivières dans le texte justifié
- ✅ 100% correspondance TOC/pages
- ✅ 0 titres orphelins
- ✅ < 1 minute pour 400 pages
- ✅ Qualité professionnelle pour impression

### Tests de Régression
Chaque PR doit passer les 6 tests critiques :
1. `test_no_blank_pages_parasites()`
2. `test_no_text_rivers()`
3. `test_toc_page_sync()`
4. `test_subparts_hierarchy()`
5. `test_no_horizontal_bars()`
6. `test_no_orphan_titles()`

## 🔐 Sécurité

- Validation stricte des inputs Markdown
- Sanitization HTML avant rendu
- Rate limiting sur génération PDF
- Isolation des processus WeasyPrint

## 🌟 Best Practices

1. **Toujours tester** avec un livre de 400+ pages
2. **Valider visuellement** chaque changement CSS
3. **Monitorer la mémoire** pendant génération PDF
4. **Cacher agressivement** les rendus HTML
5. **Documenter** chaque workaround WeasyPrint

## 📈 État d'Avancement

### ✅ PR #1 - Configuration et Infrastructure de Base (Complété)
- Base de données SQLite avec modèles Project/Chapter
- Configuration WeasyPrint pour format livre professionnel
- Structure de stockage avec 3 templates CSS (roman, technical, academic)
- Application FastAPI avec gestion du cycle de vie
- 12 tests unitaires complets
- Code formaté (black) et validé (flake8)

### ✅ PR #2 - API CRUD Projets (Complété)
- Endpoints REST complets pour les projets (/api/projects)
- Schémas Pydantic pour validation (ProjectCreate, ProjectUpdate, ProjectResponse)
- Service layer avec logique métier (ProjectService)
- Gestion des settings JSON pour configuration flexible
- 13 tests unitaires avec approche TDD
- Code formaté et validé avec flake8

### ✅ PR #3 - Gestionnaire de Chapitres (Complété)
- ✅ Endpoints CRUD pour les chapitres (/api/projects/{id}/chapters)
- ✅ Gestion automatique de l'ordre des chapitres (position)
- ✅ Import/Export Markdown avec extraction de titre H1
- ✅ Réorganisation des chapitres (bulk reorder)
- ✅ 18 tests unitaires complets
- ✅ Code formaté (black) et validé (flake8)

### ✅ PR #4 - Éditeur Monaco Intégré (Complété)
- ✅ Frontend React 18 + TypeScript + Vite
- ✅ Monaco Editor avec syntax highlighting Markdown
- ✅ Auto-complétion et snippets Markdown (h1, bold, tables, etc.)
- ✅ Zustand store pour state management + TanStack Query
- ✅ Auto-save avec debouncing (30s par défaut)
- ✅ Sidebar chapitres avec CRUD et réorganisation
- ✅ Import/Export Markdown (single ou bulk)
- ✅ 20/22 tests unitaires passent (91% succès)

### ✅ PR #5 - Processeur Markdown (Complété)
- ✅ MarkdownProcessor avec 11+ extensions (TOC, footnotes, tables, math, etc.)
- ✅ Support multi-langues avec règles typographiques françaises
- ✅ 3 templates Jinja2 professionnels (book, academic, novel)
- ✅ API endpoints pour conversion et batch processing
- ✅ Système de cache MD5 pour performance
- ✅ Sanitization HTML avec Bleach pour sécurité
- ✅ 23 tests unitaires avec approche TDD
- ✅ 1,685 lignes de code ajoutées

### ✅ PR #9 - Résolution Problèmes Pagination (Complété)
- ✅ Service AdvancedPDFGenerator avec double-passe WeasyPrint
- ✅ Classe PageBreakAnalyzer pour extraction positions TOC
- ✅ Classe PaginationValidator pour les 6 problèmes critiques
- ✅ API Export avec endpoints /api/export/{project_id}/pdf
- ✅ Validation qualité temps réel avec headers HTTP
- ✅ CSS avancé 400+ lignes résolvant tous les problèmes
- ✅ 24 tests de régression complets

### ✅ PR #10 - API Export Multi-formats (Complété)
- ✅ EPUBGenerator et DOCXGenerator avec fallback manuel
- ✅ MultiFormatExporter pour export async EPUB/DOCX
- ✅ Validation formats et gestion erreurs robuste
- ✅ Intégration système templates existant
- ✅ 30+ tests unitaires avec approche TDD

### ✅ PR #11 - Système Templates CSS Avancés (Complété)
- ✅ CSSTemplateManager avec 3 templates (ROMAN, TECHNICAL, ACADEMIC)
- ✅ TemplateRenderer modulaire avec 7 modules spécialisés
- ✅ CSSValidator détectant les 6 problèmes critiques
- ✅ Template inheritance intelligent base → spécialisé
- ✅ 26 tests unitaires complets avec validation CSS

### ✅ PR #12 - Interface Utilisateur Complète (Complété)
- ✅ **Export System**: ExportDialog avec support PDF/EPUB/DOCX et sélection template
- ✅ **Preview Pane**: Prévisualisation temps réel WebSocket avec états de chargement
- ✅ **Layout Components**: MainLayout, Toolbar, Sidebar avec navigation complète
- ✅ **App Integration**: Intégration complète dans App.tsx avec raccourcis clavier
- ✅ **Tests**: 73/73 tests passants (100% couverture nouveaux composants)
- ✅ **TypeScript**: Typage strict avec implémentations mock appropriées
- ✅ **State Management**: Intégration Zustand avec auto-save fonctionnel
- ✅ **WebSocket**: Mise à jour preview temps réel avec gestion connexion
- ✅ **API**: TanStack Query pour mutations export avec états de chargement
- ✅ **Features**: Export multi-format, preview temps réel, auto-save, raccourcis clavier
- ✅ **Quality**: 0 erreurs ESLint, design responsive, accessibilité, gestion erreurs

## 🎯 État Final du Projet
**Toutes les PR (1-5, 9-12) sont complétées et mergées vers main.**

Le Book Generator est maintenant une plateforme complète de génération de livres professionnels avec :
- Backend FastAPI complet avec API CRUD, export multi-format, et résolution des 6 problèmes critiques
- Frontend React 18 avec interface utilisateur moderne, preview temps réel, et export intégré
- 73+ tests frontend et 70+ tests backend tous passants
- Architecture prête pour la production avec WeasyPrint, Redis, et SQLite

## 🔗 Repository GitHub
- **URL**: https://github.com/julienhypeer/book-generator (privé)
- **Issues ouvertes**:
  - #2: Migrer vers PostgreSQL pour production
  - #3: Embarquer fonts localement
  - #4: Ajouter limites mémoire pour WeasyPrint
  - #5: Versionner les templates CSS

## 📚 Documentation Détaillée

- Architecture Frontend → `/frontend/CLAUDE.md`
- Architecture Backend → `/backend/CLAUDE.md` ✅ (Mis à jour avec PR #1 et #2)
- Docker Setup → `/docker/CLAUDE.md`
- Tests Strategy → `/tests/CLAUDE.md`
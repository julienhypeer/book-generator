# Générateur de Livres PDF Professionnel - Nouveau Projet

## 📚 Contexte et Retour d'Expérience

### Projet Précédent ("Livre IA") - Enseignements
**Architecture testée :**
```
21 chapitres Markdown → HTML stylé → Chrome headless → PDF (415 pages)
```

**Ce qui fonctionnait :**
- Pipeline en 3 étapes validé
- Format livre professionnel (15.6×23.39cm)
- 88,723 mots traités avec succès
- Simplicité d'usage : une seule commande

**Évolutions techniques testées :**
- ❌ ReportLab : symboles markdown persistants
- ❌ wkhtmltopdf : pas de numéros de page
- ❌ Chrome headless : problèmes de mise en page

## 🚨 Problèmes Critiques Identifiés (Projet Précédent)

### Retour d'Expérience : Projet "Livre IA" (415 pages)
**Architecture testée :** 21 chapitres Markdown → HTML → Chrome headless → PDF

### 6 Problèmes Majeurs Rencontrés

#### 1. **Pages blanches parasites (non éditoriales)**
Chrome génère des pages vides **non contrôlées** et **non intentionnelles**, différentes des pages blanches éditoriales obligatoires (verso titre, séparations chapitres, etc.)

#### 2. **Espacement entre les mots (justification)**
Justification qui crée des "rivières" blanches, pas de césure française

#### 3. **Correspondance sommaire ↔ numéros de page**
Le TOC généré ne correspond pas aux vraies pages du PDF final

#### 4. **Gestion des sous-parties**
Hiérarchie mal respectée, breaks de page aléatoires

#### 5. **Barres horizontales parasites**
Apparition de lignes horizontales en fin de chapitre (problème Chrome CSS)

#### 6. **Titres orphelins**
Titres seuls en bas de page sans contenu (manque de contrôle `page-break-after: avoid`)

### Historique des Tentatives (15+ essais)
- ❌ **ReportLab** : Symboles markdown persistants (#, ##)
- ❌ **wkhtmltopdf** : Pas de numéros de page automatiques
- ⚠️ **Chrome headless** : "Fonctionne" mais fragile, nécessite fallback manuel

### Signaux d'Instabilité Détectés
- Système nécessitant des "instructions de fallback"
- CSS embarqué dans le code Python (maintenance difficile)
- 15+ tentatives = approche chaotique
- Qualité "acceptable" mais pas professionnelle

## 💡 Insights Techniques

### Pourquoi Markdown → PDF direct échoue
- Tentative précédente de conversion directe = échec
- Markdown n'a pas de contrôle de mise en page
- Outils simples (mdpdf, etc.) trop limités

### Architecture HTML intermédiaire = Bonne approche
- Séparation contenu / style / rendu
- Contrôle total du CSS
- **Le problème n'est pas l'architecture, c'est le choix du moteur final**

## 🎯 Nouveau Projet - Plateforme Intégrée

### Vision : Rédaction + Mise en Page Unifiée
**Fonctionnalités principales :**
- **Éditeur** : Interface de rédaction moderne (Monaco Editor)
- **Prévisualisation** : Rendu temps réel de la mise en page
- **Export** : Génération PDF professionnelle

### Architecture Complète
```
Interface Web/Desktop
├── Éditeur Markdown/HTML
├── Gestionnaire Chapitres  
├── Prévisualisation Live
└── Export PDF/EPUB
```

### Moteur Principal : WeasyPrint
**Pourquoi :** Résout directement les 4 problèmes identifiés
- CSS Paged Media natif
- Césure française automatique  
- Justification professionnelle
- Contrôle précis de la pagination

## 🏗️ Structure du Nouveau Projet

```
book-writer-publisher/
├── frontend/                        # Interface de rédaction
│   ├── components/
│   │   ├── Editor/
│   │   │   ├── MarkdownEditor.jsx   # Monaco Editor configuré
│   │   │   ├── ChapterManager.jsx   # Gestion structure livre
│   │   │   └── LivePreview.jsx      # Aperçu temps réel
│   │   ├── Layout/
│   │   │   ├── TemplateSelector.jsx # Choix styles
│   │   │   ├── PageSetup.jsx        # Configuration pages
│   │   │   └── TOCManager.jsx       # Gestion sommaire
│   │   └── Export/
│   │       ├── PDFPreview.jsx       # Prévisualisation finale
│   │       └── ExportOptions.jsx    # Options export
│   └── app.jsx
├── backend/                         # Moteur de mise en page
│   ├── api/
│   │   ├── editor_api.py           # API édition/sauvegarde
│   │   ├── preview_api.py          # API prévisualisation
│   │   └── export_api.py           # API génération PDF
│   ├── core/
│   │   ├── markdown_processor.py    # Parser chapitres
│   │   ├── html_assembler.py        # Assemblage HTML
│   │   └── pdf_generator.py         # WeasyPrint + fallbacks
│   ├── templates/
│   │   ├── book_weasy.css          # CSS optimisé WeasyPrint
│   │   ├── book_pandoc.latex       # Template LaTeX
│   │   └── editor.css              # Styles éditeur
│   └── utils/
│       ├── toc_generator.py        # TOC précis en 2 passes
│       ├── page_manager.py         # Gestion pages blanches
│       └── typography.py           # Césure et justification
├── storage/                        # Stockage projets
│   ├── projects/                   # Projets utilisateur
│   └── templates/                  # Templates prédéfinis
└── config/
    └── app.yaml                    # Configuration application
```

## 🚀 Plan de Développement

### Phase 1 : Interface Rédaction (3-4 semaines)
- [ ] **Frontend React** : Interface moderne avec Monaco Editor
- [ ] **Gestionnaire Chapitres** : Création, réorganisation, navigation
- [ ] **API Backend** : Sauvegarde/chargement projets
- [ ] **Prévisualisation HTML** : Rendu basique temps réel

### Phase 2 : Moteur Mise en Page (2-3 semaines)
- [ ] **Processeur Markdown** : Parser chapitres avec métadonnées
- [ ] **Assembleur HTML** : Compilation document complet
- [ ] **WeasyPrint Integration** : Générateur PDF optimisé
- [ ] **Prévisualisation PDF** : Aperçu mise en page finale

### Phase 3 : Résolution des 6 Problèmes Identifiés (2 semaines)
- [ ] **TOC synchronisé** : Génération en 2 passes avec vrais numéros
- [ ] **Gestion pages blanches éditoriales** : Contrôle précis des pages blanches **volontaires** (verso titre, fin chapitres) vs **parasites** (bugs Chrome)
- [ ] **Typographie avancée** : Césure française + justification sans rivières
- [ ] **Hiérarchie intelligente** : Gestion sous-parties avec breaks appropriés
- [ ] **Élimination barres horizontales** : CSS propre sans artifacts
- [ ] **Protection titres orphelins** : `page-break-after: avoid` + contrôles CSS

### Phase 4 : Fonctionnalités Avancées (2 semaines)
- [ ] **Templates multiples** : Styles prédéfinis
- [ ] **Configuration pages** : Marges, format, polices
- [ ] **Export multi-formats** : PDF, EPUB, DOCX
- [ ] **Mode collaboratif** : Partage/commentaires (optionnel)

## 🎯 Objectifs Techniques

### Résolution des 6 Problèmes Spécifiques
1. ✅ **Pages blanches éditoriales** : Contrôle précis des pages blanches **volontaires** vs **parasites**
2. ✅ **Espacement mots** : Césure française + justification professionnelle  
3. ✅ **TOC synchronisé** : Génération en 2 passes avec vrais numéros
4. ✅ **Sous-parties** : Hiérarchie CSS + compteurs intelligents
5. ✅ **Barres horizontales** : CSS clean sans artifacts Chrome
6. ✅ **Titres orphelins** : Protection `page-break-after: avoid` native

### Critères de Succès
- **Qualité professionnelle** : Zéro des 6 problèmes identifiés
- **Simplicité** : Interface intuitive vs 15+ tentatives précédentes
- **Fiabilité** : Système stable sans fallback manuel
- **Performance** : < 1 minute pour 400 pages (référence : 415 pages testées)

## 🛠️ Stack Technique

**Frontend :** React + Monaco Editor + Tailwind
**Backend :** Python FastAPI + WebSockets
**Moteur PDF :** WeasyPrint
**Base données :** SQLite (projets) + FileSystem (contenu)
**Interface :** Web (responsive) + Electron (desktop optionnel)

**Dépendances clés :**
```python
# Backend
fastapi>=0.100.0
weasyprint>=59.0
markdown>=3.4
websockets>=11.0

# Frontend  
@monaco-editor/react
@tailwindcss/typography
react-split-pane
```

## 💭 Vision Produit

Créer une plateforme complète d'écriture et publication qui combine :
- **L'expérience d'écriture** d'un éditeur moderne (VS Code, Notion)
- **La qualité de mise en page** d'un logiciel professionnel (InDesign)
- **La simplicité d'usage** d'un outil web moderne

**Workflow cible :**
1. **Écrire** : Interface intuitive, gestion chapitres
2. **Ajuster** : Prévisualisation temps réel de la mise en page  
3. **Publier** : Export PDF professionnel en un clic

**Différenciation :** Résout les 6 problèmes spécifiques identifiés sur 415 pages réelles :
- Pages blanches **éditoriales** non contrôlées vs **parasites** (bugs moteur)  
- Rivières dans la justification  
- TOC désynchronisé
- Sous-parties mal gérées
- Barres horizontales en fin de chapitre
- Titres orphelins en bas de page

Plus jamais de 15+ tentatives ou de systèmes de fallback manuel.
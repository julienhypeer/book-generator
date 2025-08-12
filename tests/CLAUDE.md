# 🧪 Tests - Instructions Claude

## 📋 Contexte
Stratégie de tests pour garantir la qualité professionnelle des PDFs générés.

## 🎯 Tests Critiques (6 Problèmes)

### 1. Test Pages Blanches Parasites
```python
def test_no_blank_pages_parasites():
    """Vérifie qu'il n'y a QUE des pages blanches éditoriales"""
    pdf = generate_test_book()
    blank_pages = extract_blank_pages(pdf)
    
    # Pages blanches attendues (éditoriales)
    expected_blanks = {2, 4, 50, 102}  # Verso titre, fin parties
    
    # Aucune page blanche parasite
    assert blank_pages == expected_blanks
```

### 2. Test Rivières Blanches
```python
def test_no_text_rivers():
    """Vérifie l'absence de rivières dans la justification"""
    pdf = generate_test_book()
    
    for page in pdf.pages:
        text_blocks = extract_text_blocks(page)
        rivers = detect_rivers(text_blocks)
        assert len(rivers) == 0, f"Rivière détectée page {page.num}"
```

### 3. Test Synchronisation TOC
```python
def test_toc_page_sync():
    """Vérifie que le TOC pointe vers les bonnes pages"""
    pdf = generate_test_book()
    toc_entries = extract_toc(pdf)
    
    for entry in toc_entries:
        actual_page = find_heading_page(pdf, entry.title)
        assert entry.page == actual_page, \
            f"TOC désynchronisé: {entry.title}"
```

### 4. Test Hiérarchie Sous-Parties
```python
def test_subparts_hierarchy():
    """Vérifie la hiérarchie et les page-breaks"""
    pdf = generate_test_book()
    
    # Vérifier numérotation
    assert "1.1" in pdf.text  # Sous-section existe
    assert "1.1.1" in pdf.text  # Sous-sous-section
    
    # Vérifier page-breaks
    h2_positions = find_all_h2_positions(pdf)
    for pos in h2_positions:
        assert not is_at_bottom_of_page(pos)
```

### 5. Test Barres Horizontales
```python
def test_no_horizontal_bars():
    """Vérifie l'absence de barres parasites"""
    pdf = generate_test_book()
    
    for page in pdf.pages:
        artifacts = detect_visual_artifacts(page)
        horizontal_lines = [a for a in artifacts 
                           if a.type == 'horizontal_line']
        assert len(horizontal_lines) == 0
```

### 6. Test Titres Orphelins
```python
def test_no_orphan_titles():
    """Vérifie qu'aucun titre n'est orphelin"""
    pdf = generate_test_book()
    
    for page in pdf.pages:
        titles = extract_titles(page)
        for title in titles:
            if is_near_bottom(title.position):
                # Vérifier qu'il y a du contenu après
                content_after = get_content_after(title)
                assert len(content_after) > 50  # Au moins 50 chars
```

## 🧪 Tests de Performance

### Test Génération 400 Pages
```python
@pytest.mark.performance
def test_large_book_generation():
    """Génération < 1 minute pour 400 pages"""
    start = time.time()
    
    book = create_book_with_pages(400)
    pdf = generate_pdf(book)
    
    duration = time.time() - start
    assert duration < 60  # Moins d'1 minute
    assert pdf.page_count == 400
```

### Test Mémoire
```python
@pytest.mark.memory
def test_memory_usage():
    """Vérifier que la mémoire ne dépasse pas 2GB"""
    import tracemalloc
    tracemalloc.start()
    
    generate_pdf(create_large_book())
    
    current, peak = tracemalloc.get_traced_memory()
    assert peak < 2 * 1024 * 1024 * 1024  # < 2GB
```

## 🎨 Tests Visuels

### Visual Regression
```python
def test_visual_regression():
    """Compare avec PDF de référence"""
    new_pdf = generate_test_book()
    reference_pdf = load_reference_pdf()
    
    diff = visual_diff(new_pdf, reference_pdf)
    assert diff.similarity > 0.99  # 99% similaire
```

### Test Polices
```python
def test_fonts_rendering():
    """Vérifie le rendu des polices"""
    pdf = generate_test_book()
    fonts = extract_fonts(pdf)
    
    assert 'Liberation Serif' in fonts
    assert 'DejaVu Sans' in fonts
    # Pas de font fallback générique
    assert 'Times' not in fonts
```

## 🔧 Fixtures

### Livre de Test Standard
```python
@pytest.fixture
def standard_book():
    """Livre avec tous les cas edge"""
    return {
        'title': 'Test Book',
        'chapters': [
            {'title': 'Chapter 1', 'content': LONG_TEXT},
            {'title': 'Chapter 2', 'subsections': [
                {'title': '2.1', 'content': SHORT_TEXT},
                {'title': '2.2', 'content': MEDIUM_TEXT}
            ]},
            # ... 21 chapitres comme le projet réel
        ]
    }
```

### Configurations de Test
```python
@pytest.fixture
def weasyprint_config():
    """Config WeasyPrint pour tests"""
    return {
        'stylesheets': ['tests/fixtures/test.css'],
        'font_config': FontConfiguration(),
        'pdf_variant': 'pdf/a-3b'  # Pour archivage
    }
```

## 📊 Coverage Requirements

```yaml
coverage:
  minimum: 80%
  critical_paths: 100%  # Les 6 problèmes
  exclude:
    - "*/migrations/*"
    - "*/tests/*"
```

## 🚀 CI/CD Integration

### GitHub Actions
```yaml
- name: Run Critical Tests
  run: |
    pytest tests/critical/ -v
    pytest tests/regression/ --visual
    pytest tests/performance/ --benchmark

- name: Check PDF Quality
  run: |
    python tests/pdf_validator.py output.pdf
```

## 🔧 Commandes

```bash
# Tests unitaires
pytest tests/unit/

# Tests intégration
pytest tests/integration/

# Tests E2E
pytest tests/e2e/ --headed

# Tests avec coverage
pytest --cov=app --cov-report=html

# Tests de performance
pytest tests/performance/ -v --benchmark-only

# Tests visuels
pytest tests/visual/ --visual-regression
```

## 📈 Benchmarks

### Temps de Génération Cibles
- 10 pages : < 2s
- 100 pages : < 15s
- 400 pages : < 60s
- 1000 pages : < 3min

### Qualité PDF Cibles
- DPI : 300 minimum
- Compression : < 100KB/page
- Fonts embedded : 100%
- PDF/A compliant : Oui
"""
Tests de régression pour les 6 problèmes critiques de pagination.
Tests complets pour valider la résolution des problèmes identifiés.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import re

# Mock WeasyPrint depuis le début
mock_weasyprint = MagicMock()
mock_html = MagicMock()
mock_document = MagicMock()
mock_page = MagicMock()

# Configuration des mocks
mock_document.pages = [mock_page]
mock_document.write_pdf.return_value = b"fake_pdf_content"
mock_html.render.return_value = mock_document
mock_weasyprint.HTML.return_value = mock_html
mock_page._page_box.get_elements_by_tag.return_value = []
mock_page._page_box.get_text.return_value = "Test content"
mock_page.height = 800

with patch.dict('sys.modules', {'weasyprint': mock_weasyprint}):
    from app.services.pdf_generator import (
        AdvancedPDFGenerator, 
        PageBreakAnalyzer, 
        PaginationValidator
    )
    from app.models.project import Project
    from app.models.chapter import Chapter


class TestPageBreakAnalyzer:
    """Tests pour l'analyseur de sauts de page."""
    
    @pytest.fixture
    def analyzer(self):
        return PageBreakAnalyzer()
    
    def test_extract_page_positions(self, analyzer):
        """Test extraction des positions de titres."""
        # Mock document avec éléments
        mock_element = MagicMock()
        mock_element.id = "heading-chapter-1"
        
        # Premier page avec élément
        mock_page1 = MagicMock()
        mock_page1._page_box.get_elements_by_tag.return_value = [mock_element]
        
        # Deuxième page sans éléments
        mock_page2 = MagicMock()
        mock_page2._page_box.get_elements_by_tag.return_value = []
        
        mock_document.pages = [mock_page1, mock_page2]
        
        page_map = analyzer.extract_page_positions(mock_document)
        
        assert isinstance(page_map, dict)
        assert "heading-chapter-1" in page_map
        assert page_map["heading-chapter-1"] == 1
    
    def test_generate_toc_entries(self, analyzer):
        """Test génération des entrées TOC."""
        html = """
        <h1 id="chapter-1">Introduction</h1>
        <p>Content...</p>
        <h2 id="section-1">Section 1</h2>
        <p>More content...</p>
        <h3 id="subsection-1">Subsection 1.1</h3>
        """
        
        entries = analyzer.generate_toc_entries(html)
        
        assert len(entries) == 3
        assert entries[0]['level'] == 1
        assert entries[0]['title'] == 'Introduction'
        assert entries[1]['level'] == 2
        assert entries[2]['level'] == 3


class TestPaginationValidator:
    """Tests pour le validateur de pagination."""
    
    @pytest.fixture
    def validator(self):
        return PaginationValidator()
    
    def test_validate_no_blank_parasites_valid(self, validator):
        """Test détection pages blanches - cas valide."""
        # Mock page avec contenu
        mock_page._page_box.get_text.return_value = "Chapter content here"
        mock_document.pages = [mock_page]
        
        result = validator.validate_no_blank_parasites(mock_document)
        
        assert result['valid'] is True
        assert len(result['blank_parasites']) == 0
    
    def test_validate_no_blank_parasites_with_parasites(self, validator):
        """Test détection pages blanches - cas avec parasites."""
        # Mock page vide (parasite)
        mock_blank_page = MagicMock()
        mock_blank_page._page_box.get_text.return_value = ""
        
        # Mock page avec contenu normal
        mock_content_page = MagicMock()
        mock_content_page._page_box.get_text.return_value = "Real content"
        
        mock_document.pages = [mock_content_page, mock_blank_page]
        
        result = validator.validate_no_blank_parasites(mock_document)
        
        assert result['valid'] is False
        assert 2 in result['blank_parasites']  # Page 2 est vide
    
    def test_detect_text_rivers(self, validator):
        """Test détection des rivières de texte."""
        # Mock paragraphe long avec mots courts (risque de rivières)
        mock_paragraph = MagicMock()
        mock_paragraph.get_text.return_value = "A B C D E F G H I J " * 20  # Mots très courts
        
        mock_page._page_box.get_elements_by_tag.return_value = [mock_paragraph]
        mock_document.pages = [mock_page]
        
        result = validator.detect_text_rivers(mock_document)
        
        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'river_count' in result
    
    def test_validate_toc_sync_perfect(self, validator):
        """Test synchronisation TOC - cas parfait."""
        page_map = {
            "heading-1": 1,
            "heading-2": 3,
            "heading-3": 5
        }
        
        toc_entries = [
            {'id': 'heading-1', 'title': 'Chapter 1', 'page': 1},
            {'id': 'heading-2', 'title': 'Chapter 2', 'page': 3},
            {'id': 'heading-3', 'title': 'Chapter 3', 'page': 5}
        ]
        
        result = validator.validate_toc_sync(page_map, toc_entries)
        
        assert result['valid'] is True
        assert len(result['mismatches']) == 0
    
    def test_validate_toc_sync_mismatch(self, validator):
        """Test synchronisation TOC - cas avec désynchronisation."""
        page_map = {
            "heading-1": 1,
            "heading-2": 4,  # Vraie position
        }
        
        toc_entries = [
            {'id': 'heading-1', 'title': 'Chapter 1', 'page': 1},
            {'id': 'heading-2', 'title': 'Chapter 2', 'page': 3},  # Mauvaise page dans TOC
        ]
        
        result = validator.validate_toc_sync(page_map, toc_entries)
        
        assert result['valid'] is False
        assert len(result['mismatches']) == 1
        assert result['mismatches'][0]['expected'] == 4
        assert result['mismatches'][0]['actual'] == 3
    
    def test_detect_orphan_titles(self, validator):
        """Test détection des titres orphelins."""
        # Mock titre en position basse sans contenu après
        mock_title = MagicMock()
        mock_title.get_text.return_value = "Lonely Title"
        mock_title.position_y = 700  # Proche du bas (page height = 800)
        mock_title.get_next_siblings.return_value = []  # Pas de contenu après
        
        mock_page.height = 800
        mock_page._page_box.get_elements_by_tag.return_value = [mock_title]
        mock_document.pages = [mock_page]
        
        result = validator.detect_orphan_titles(mock_document)
        
        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'orphan_titles' in result


class TestAdvancedPDFGenerator:
    """Tests pour le générateur PDF avancé."""
    
    @pytest.fixture
    def generator(self):
        return AdvancedPDFGenerator()
    
    def test_generate_advanced_css(self, generator):
        """Test génération CSS avancé."""
        css = generator.generate_advanced_css('roman')
        
        # Vérifier que le CSS contient les règles critiques
        assert '@page' in css
        assert 'hyphens: auto' in css  # Problème #2: césure
        assert 'page-break-after: avoid' in css  # Problème #6: orphelins
        assert 'counter-increment:' in css  # Problème #4: hiérarchie
        assert 'hr {' in css and 'display: none' in css  # Problème #5: barres horizontales
        assert 'orphans:' in css and 'widows:' in css  # Protection générale
    
    def test_preprocess_html_adds_anchors(self, generator):
        """Test préprocessing HTML - ajout d'ancres."""
        html = '<h1>Chapter Title</h1><p>Content</p>'
        
        processed = generator.preprocess_html(html)
        
        assert 'id="heading-Chapter Title"' in processed
        assert 'data-anchor="heading-Chapter Title"' in processed
    
    def test_preprocess_html_removes_hr_tags(self, generator):
        """Test préprocessing HTML - suppression des <hr>."""
        html = '<p>Before</p><hr><p>After</p><hr/><p>End</p>'
        
        processed = generator.preprocess_html(html)
        
        # Vérifier que <hr> sont remplacés par des séparateurs sémantiques
        assert '<hr>' not in processed
        assert '<hr/>' not in processed
        assert 'chapter-separator' in processed
    
    def test_preprocess_html_first_paragraphs(self, generator):
        """Test préprocessing HTML - marquage premiers paragraphes."""
        html = '<h1>Chapter</h1><p>First paragraph</p><p>Second paragraph</p>'
        
        processed = generator.preprocess_html(html)
        
        assert 'class="first-paragraph"' in processed
    
    def test_inject_toc_pages(self, generator):
        """Test injection des numéros de page dans TOC."""
        html = '''
        <div class="toc-entry">
            <span class="toc-title">Chapter 1</span>
            <span class="toc-page" data-anchor="heading-1">?</span>
        </div>
        '''
        
        page_map = {'heading-1': 5}
        
        result = generator.inject_toc_pages(html, page_map)
        
        assert '<span class="toc-page">5</span>' in result
        assert 'data-anchor' not in result  # Nettoyé après injection
    
    @pytest.mark.asyncio
    async def test_generate_pdf_two_pass_success(self, generator):
        """Test génération PDF double-passe - cas de succès."""
        html = '<h1 id="ch1">Chapter 1</h1><p>Content here</p>'
        
        # Mock WeasyPrint disponible et génération PDF
        with patch('app.services.pdf_generator.WEASYPRINT_AVAILABLE', True):
            with patch.object(generator.analyzer, 'extract_page_positions') as mock_extract:
                with patch('app.services.pdf_generator.HTML') as mock_html_class:
                    mock_extract.return_value = {'ch1': 1}
                    
                    # Mock la génération PDF
                    mock_html = MagicMock()
                    mock_document = MagicMock()
                    mock_document.pages = [mock_page]
                    mock_document.write_pdf.return_value = b"fake_pdf_content"
                    mock_html.render.return_value = mock_document
                    mock_html_class.return_value = mock_html
                    
                    pdf_bytes, metadata = await generator.generate_pdf_two_pass(html)
        
        assert isinstance(pdf_bytes, bytes)
        assert 'page_count' in metadata
        assert 'page_map' in metadata
        assert 'quality_validation' in metadata
        assert metadata['page_map'] == {'ch1': 1}
    
    @pytest.mark.asyncio
    async def test_generate_from_project_with_toc(self, generator):
        """Test génération depuis un projet avec TOC."""
        # Mock project
        project = Mock()
        project.title = "Test Book"
        project.settings = {'table_of_contents': True}
        
        # Mock chapters
        chapter1 = Mock()
        chapter1.title = "Introduction"
        chapter1.content = "<p>Introduction content</p>"
        chapter1.position = 1
        
        chapter2 = Mock()
        chapter2.title = "Chapter 1"
        chapter2.content = "<p>Chapter 1 content</p>"
        chapter2.position = 2
        
        chapters = [chapter1, chapter2]
        
        with patch.object(generator, 'generate_pdf_two_pass') as mock_generate:
            mock_generate.return_value = (b"pdf_content", {"page_count": 10})
            
            pdf_bytes, metadata = await generator.generate_from_project(project, chapters)
        
        # Vérifier que generate_pdf_two_pass a été appelé
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args[0]
        html_content = call_args[0]
        
        # Vérifier que TOC est inclus
        assert "Table des matières" in html_content
        assert "Introduction" in html_content
        assert "Chapter 1" in html_content
        
        # Vérifier structure des chapitres
        assert '<div class="chapter">' in html_content


class TestCriticalProblemsIntegration:
    """Tests d'intégration pour les 6 problèmes critiques."""
    
    @pytest.fixture
    def generator(self):
        return AdvancedPDFGenerator()
    
    def test_problem_1_blank_pages_prevention(self, generator):
        """Test Problème #1: Prévention des pages blanches parasites."""
        css = generator.generate_advanced_css()
        
        # Vérifier règles CSS spécifiques (flexibles avec espaces)
        assert '.chapter-end' in css and 'page-break-after: right' in css
        assert '.part-separator' in css and 'page-break-before: right' in css
        assert '.editorial-break' in css
    
    def test_problem_2_text_rivers_prevention(self, generator):
        """Test Problème #2: Prévention des rivières de texte."""
        css = generator.generate_advanced_css()
        
        # Vérifier configuration césure française optimale
        assert 'hyphens: auto;' in css
        assert 'hyphenate-language: "fr";' in css
        assert 'hyphenate-limit-chars: 6 3 3;' in css
        assert 'hyphenate-limit-lines: 2;' in css
        assert 'word-spacing: 0.16em;' in css
        assert 'text-justify: inter-word;' in css
    
    def test_problem_3_toc_synchronization(self, generator):
        """Test Problème #3: Synchronisation TOC."""
        html = '<h1 id="ch1">Chapter 1</h1>'
        page_map = {'ch1': 5}
        
        # Test injection des numéros
        toc_html = '<span class="toc-page" data-anchor="ch1">?</span>'
        result = generator.inject_toc_pages(toc_html, page_map)
        
        assert '<span class="toc-page">5</span>' in result
    
    def test_problem_4_hierarchy_counters(self, generator):
        """Test Problème #4: Hiérarchie avec compteurs CSS."""
        css = generator.generate_advanced_css()
        
        # Vérifier compteurs CSS
        assert 'counter-reset: chapter section subsection;' in css
        assert 'h1 {' in css and 'counter-increment: chapter;' in css
        assert 'h2 {' in css and 'counter-increment: section;' in css
        assert 'h3 {' in css and 'counter-increment: subsection;' in css
        
        # Vérifier affichage des numéros
        assert 'h1::before {' in css
        assert 'content: "Chapitre " counter(chapter)' in css
        assert 'h2::before {' in css
        assert 'content: counter(chapter) "." counter(section)' in css
    
    def test_problem_5_horizontal_bars_removal(self, generator):
        """Test Problème #5: Suppression barres horizontales."""
        css = generator.generate_advanced_css()
        html = '<p>Before</p><hr><p>After</p>'
        
        # CSS doit cacher les <hr> (flexible avec espaces)
        assert 'hr' in css and 'display: none' in css
        
        # HTML preprocessing doit remplacer <hr>
        processed = generator.preprocess_html(html)
        assert '<hr>' not in processed
        assert 'chapter-separator' in processed
    
    def test_problem_6_orphan_titles_protection(self, generator):
        """Test Problème #6: Protection des titres orphelins."""
        css = generator.generate_advanced_css()
        
        # Vérifier règles de protection
        assert 'h1, h2, h3, h4, h5, h6 {' in css
        assert 'page-break-after: avoid;' in css
        assert 'page-break-inside: avoid;' in css
        assert 'orphans: 4;' in css
        assert 'widows: 4;' in css
        assert 'min-height: 2.5em;' in css  # Assure espace minimum


class TestPDFQualityValidation:
    """Tests pour la validation de qualité PDF."""
    
    @pytest.fixture
    def generator(self):
        return AdvancedPDFGenerator()
    
    @pytest.mark.asyncio
    async def test_quality_validation_all_pass(self, generator):
        """Test validation qualité - tous les checks passent."""
        html = '<h1>Perfect Chapter</h1><p>Perfect content with good typography.</p>'
        
        # Mock validator pour retourner tous les checks valides
        with patch.object(generator.validator, 'validate_no_blank_parasites') as mock_blank:
            with patch.object(generator.validator, 'detect_text_rivers') as mock_rivers:
                with patch.object(generator.validator, 'validate_toc_sync') as mock_toc:
                    with patch.object(generator.validator, 'detect_orphan_titles') as mock_orphans:
                        
                        mock_blank.return_value = {'valid': True, 'blank_parasites': []}
                        mock_rivers.return_value = {'valid': True, 'river_count': 0}
                        mock_toc.return_value = {'valid': True, 'mismatches': []}
                        mock_orphans.return_value = {'valid': True, 'orphan_titles': []}
                        
                        pdf_bytes, metadata = await generator.generate_pdf_two_pass(html)
        
        # Vérifier que tous les checks ont passé
        assert metadata['all_checks_passed'] is True
        quality = metadata['quality_validation']
        assert all(result['valid'] for result in quality.values())
    
    @pytest.mark.asyncio
    async def test_quality_validation_with_issues(self, generator):
        """Test validation qualité - avec problèmes détectés."""
        html = '<h1>Problematic Chapter</h1><hr><p>Bad content</p>'
        
        # Mock validator pour retourner des problèmes
        with patch.object(generator.validator, 'validate_no_blank_parasites') as mock_blank:
            with patch.object(generator.validator, 'detect_text_rivers') as mock_rivers:
                with patch.object(generator.validator, 'validate_toc_sync') as mock_toc:
                    with patch.object(generator.validator, 'detect_orphan_titles') as mock_orphans:
                        
                        mock_blank.return_value = {'valid': False, 'blank_parasites': [3]}
                        mock_rivers.return_value = {'valid': True, 'river_count': 0}
                        mock_toc.return_value = {'valid': False, 'mismatches': [{'entry': 'test'}]}
                        mock_orphans.return_value = {'valid': True, 'orphan_titles': []}
                        
                        pdf_bytes, metadata = await generator.generate_pdf_two_pass(html)
        
        # Vérifier que des problèmes ont été détectés
        assert metadata['all_checks_passed'] is False
        quality = metadata['quality_validation']
        assert not quality['blank_pages']['valid']
        assert not quality['toc_sync']['valid']


class TestPDFEndToEnd:
    """Tests end-to-end pour génération PDF complète."""
    
    @pytest.mark.asyncio
    async def test_full_book_generation(self):
        """Test génération complète d'un livre de test."""
        generator = AdvancedPDFGenerator()
        
        # Project mock
        project = Mock()
        project.title = "Test Novel"
        project.settings = {
            'table_of_contents': True,
            'page_numbers': True,
            'hyphenation': True
        }
        
        # Chapters mock  
        chapters = []
        for i in range(1, 4):
            chapter = Mock()
            chapter.title = f"Chapter {i}"
            chapter.content = f"<p>This is the content of chapter {i}. " * 50 + "</p>"
            chapter.position = i
            chapters.append(chapter)
        
        # Test génération
        pdf_bytes, metadata = await generator.generate_from_project(project, chapters)
        
        # Vérifications de base
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert metadata['page_count'] > 0
        assert 'quality_validation' in metadata
        
        # Log results pour debug
        print(f"Generated PDF: {len(pdf_bytes)} bytes, {metadata['page_count']} pages")
        print(f"Quality validation: {metadata['all_checks_passed']}")


if __name__ == "__main__":
    # Permettre d'exécuter les tests directement
    pytest.main([__file__, "-v"])
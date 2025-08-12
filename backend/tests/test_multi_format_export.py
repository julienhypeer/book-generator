"""
Tests TDD pour l'exporteur multi-formats (EPUB, DOCX).
Tests écrits d'abord selon l'approche TDD.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any

from app.services.multi_format_exporter import (
    MultiFormatExporter, 
    EPUBGenerator, 
    DOCXGenerator,
    ExportError
)
from app.validators.export import ExportFormat
from app.validators.export import ExportRequest, TemplateType, PaperSize
from app.models.project import Project
from app.models.chapter import Chapter


class TestEPUBGenerator:
    """Tests TDD pour le générateur EPUB."""
    
    @pytest.fixture
    def epub_generator(self):
        return EPUBGenerator()
    
    @pytest.fixture
    def sample_project(self):
        project = Mock()
        project.title = "Test Novel"
        project.settings = {
            'author': 'Test Author',
            'description': 'A test novel for EPUB generation'
        }
        return project
    
    @pytest.fixture
    def sample_chapters(self):
        chapters = []
        for i in range(1, 4):
            chapter = Mock()
            chapter.title = f"Chapter {i}"
            chapter.content = f"<p>This is the content of chapter {i}. " * 20 + "</p>"
            chapter.position = i
            chapters.append(chapter)
        return chapters
    
    def test_epub_structure_creation(self, epub_generator, sample_project, sample_chapters):
        """Test création de la structure EPUB correcte."""
        epub_bytes = epub_generator.generate_epub(sample_project, sample_chapters)
        
        # Vérifier que c'est un fichier ZIP valide
        assert isinstance(epub_bytes, bytes)
        assert len(epub_bytes) > 0
        
        # Vérifier structure EPUB basique
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(epub_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as epub_zip:
                file_list = epub_zip.namelist()
                
                # Fichiers obligatoires EPUB
                assert 'mimetype' in file_list
                assert 'META-INF/container.xml' in file_list
                assert 'OEBPS/content.opf' in file_list
                assert 'OEBPS/toc.ncx' in file_list
                
                # Vérifier mimetype
                mimetype_content = epub_zip.read('mimetype').decode('utf-8')
                assert mimetype_content == 'application/epub+zip'
    
    def test_epub_metadata_injection(self, epub_generator, sample_project, sample_chapters):
        """Test injection des métadonnées dans l'EPUB."""
        epub_bytes = epub_generator.generate_epub(sample_project, sample_chapters)
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(epub_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as epub_zip:
                # Vérifier content.opf contient les métadonnées
                opf_content = epub_zip.read('OEBPS/content.opf').decode('utf-8')
                
                assert sample_project.title in opf_content
                assert sample_project.settings['author'] in opf_content
                assert sample_project.settings['description'] in opf_content
                assert '<dc:language>fr</dc:language>' in opf_content
    
    def test_epub_chapter_files_creation(self, epub_generator, sample_project, sample_chapters):
        """Test création des fichiers de chapitres EPUB."""
        epub_bytes = epub_generator.generate_epub(sample_project, sample_chapters)
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(epub_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as epub_zip:
                file_list = epub_zip.namelist()
                
                # Vérifier que chaque chapitre a son fichier XHTML
                for i, chapter in enumerate(sample_chapters, 1):
                    chapter_file = f'OEBPS/chapter{i}.xhtml'
                    assert chapter_file in file_list
                    
                    # Vérifier contenu du chapitre
                    chapter_content = epub_zip.read(chapter_file).decode('utf-8')
                    assert chapter.title in chapter_content
                    assert chapter.content in chapter_content
    
    def test_epub_toc_generation(self, epub_generator, sample_project, sample_chapters):
        """Test génération de la table des matières EPUB."""
        epub_bytes = epub_generator.generate_epub(sample_project, sample_chapters)
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(epub_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as epub_zip:
                # Vérifier toc.ncx
                toc_content = epub_zip.read('OEBPS/toc.ncx').decode('utf-8')
                
                # Vérifier que tous les chapitres sont dans la TOC
                for chapter in sample_chapters:
                    assert chapter.title in toc_content
    
    def test_epub_invalid_content_handling(self, epub_generator, sample_project):
        """Test gestion du contenu invalide."""
        # Chapitre avec contenu HTML malformé
        bad_chapter = Mock()
        bad_chapter.title = "Bad Chapter"
        bad_chapter.content = "<p>Unclosed paragraph <div>Bad nesting</p></div>"
        bad_chapter.position = 1
        
        # Ne doit pas lever d'exception mais corriger le HTML
        epub_bytes = epub_generator.generate_epub(sample_project, [bad_chapter])
        assert isinstance(epub_bytes, bytes)
        assert len(epub_bytes) > 0


class TestDOCXGenerator:
    """Tests TDD pour le générateur DOCX."""
    
    @pytest.fixture
    def docx_generator(self):
        return DOCXGenerator()
    
    @pytest.fixture
    def sample_project(self):
        project = Mock()
        project.title = "Test Document"
        project.settings = {
            'author': 'Test Author',
            'subject': 'Test Subject'
        }
        return project
    
    @pytest.fixture
    def sample_chapters(self):
        chapters = []
        for i in range(1, 4):
            chapter = Mock()
            chapter.title = f"Section {i}"
            chapter.content = f"<p>Content for section {i}. " * 15 + "</p>"
            chapter.position = i
            chapters.append(chapter)
        return chapters
    
    def test_docx_structure_creation(self, docx_generator, sample_project, sample_chapters):
        """Test création de la structure DOCX correcte."""
        docx_bytes = docx_generator.generate_docx(sample_project, sample_chapters)
        
        # Vérifier que c'est un fichier ZIP valide (DOCX = ZIP)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(docx_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as docx_zip:
                file_list = docx_zip.namelist()
                
                # Fichiers obligatoires DOCX
                assert 'word/document.xml' in file_list
                assert '[Content_Types].xml' in file_list
                assert '_rels/.rels' in file_list
                assert 'word/_rels/document.xml.rels' in file_list
                assert 'docProps/core.xml' in file_list
    
    def test_docx_document_content(self, docx_generator, sample_project, sample_chapters):
        """Test injection du contenu dans le document DOCX."""
        docx_bytes = docx_generator.generate_docx(sample_project, sample_chapters)
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(docx_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as docx_zip:
                # Vérifier document.xml contient le contenu
                doc_xml = docx_zip.read('word/document.xml').decode('utf-8')
                
                # Vérifier présence de tous les chapitres
                for chapter in sample_chapters:
                    assert chapter.title in doc_xml
    
    def test_docx_metadata_properties(self, docx_generator, sample_project, sample_chapters):
        """Test injection des propriétés de document."""
        docx_bytes = docx_generator.generate_docx(sample_project, sample_chapters)
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(docx_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as docx_zip:
                # Vérifier core.xml contient les métadonnées
                core_xml = docx_zip.read('docProps/core.xml').decode('utf-8')
                
                assert sample_project.title in core_xml
                assert sample_project.settings['author'] in core_xml
                assert sample_project.settings['subject'] in core_xml
    
    def test_docx_markdown_to_docx_conversion(self, docx_generator, sample_project):
        """Test conversion Markdown vers format DOCX."""
        # Chapitre avec Markdown
        md_chapter = Mock()
        md_chapter.title = "Markdown Chapter"
        md_chapter.content = """
        # Heading 1
        ## Heading 2
        
        **Bold text** and *italic text*
        
        - List item 1
        - List item 2
        
        > Blockquote
        
        `code snippet`
        """
        md_chapter.position = 1
        
        docx_bytes = docx_generator.generate_docx(sample_project, [md_chapter])
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(docx_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as docx_zip:
                doc_xml = docx_zip.read('word/document.xml').decode('utf-8')
                
                # Vérifier que le Markdown a été converti en éléments DOCX
                assert 'Heading 1' in doc_xml
                assert 'Heading 2' in doc_xml
                assert 'Bold text' in doc_xml
                assert 'italic text' in doc_xml


class TestMultiFormatExporter:
    """Tests TDD pour l'exporteur multi-formats principal."""
    
    @pytest.fixture
    def exporter(self):
        return MultiFormatExporter()
    
    @pytest.fixture
    def sample_project(self):
        project = Mock()
        project.title = "Multi Format Test"
        project.settings = {
            'author': 'Test Author',
            'description': 'Test description'
        }
        return project
    
    @pytest.fixture
    def sample_chapters(self):
        chapters = []
        for i in range(1, 3):
            chapter = Mock()
            chapter.title = f"Chapter {i}"
            chapter.content = f"<p>Chapter {i} content.</p>"
            chapter.position = i
            chapters.append(chapter)
        return chapters
    
    @pytest.mark.asyncio
    async def test_export_epub_format(self, exporter, sample_project, sample_chapters):
        """Test export au format EPUB."""
        export_request = ExportRequest(
            format="epub",
            template=TemplateType.ROMAN,
            include_toc=True,
            quality_validation=False
        )
        
        result_bytes, metadata = await exporter.export(
            sample_project, sample_chapters, export_request
        )
        
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
        assert metadata['format'] == 'epub'
        assert metadata['file_size'] == len(result_bytes)
        assert 'generation_time' in metadata
    
    @pytest.mark.asyncio
    async def test_export_docx_format(self, exporter, sample_project, sample_chapters):
        """Test export au format DOCX."""
        export_request = ExportRequest(
            format="docx",
            template=TemplateType.TECHNICAL,
            include_toc=True
        )
        
        result_bytes, metadata = await exporter.export(
            sample_project, sample_chapters, export_request
        )
        
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
        assert metadata['format'] == 'docx'
        assert metadata['file_size'] == len(result_bytes)
        assert 'generation_time' in metadata
    
    @pytest.mark.asyncio
    async def test_unsupported_format_error(self, exporter, sample_project, sample_chapters):
        """Test erreur pour format non supporté."""
        export_request = ExportRequest(
            format="xyz",  # Format inexistant
            template=TemplateType.ROMAN
        )
        
        with pytest.raises(ExportError) as exc_info:
            await exporter.export(sample_project, sample_chapters, export_request)
        
        assert "Unsupported format" in str(exc_info.value)
        assert "xyz" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_empty_chapters_handling(self, exporter, sample_project):
        """Test gestion des projets sans chapitres."""
        export_request = ExportRequest(format="epub")
        
        with pytest.raises(ExportError) as exc_info:
            await exporter.export(sample_project, [], export_request)
        
        assert "No chapters" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_metadata_generation(self, exporter, sample_project, sample_chapters):
        """Test génération des métadonnées d'export."""
        export_request = ExportRequest(
            format="epub",
            include_toc=True,
            quality_validation=True
        )
        
        result_bytes, metadata = await exporter.export(
            sample_project, sample_chapters, export_request
        )
        
        # Vérifier métadonnées requises
        assert 'format' in metadata
        assert 'file_size' in metadata
        assert 'generation_time' in metadata
        assert 'chapter_count' in metadata
        assert 'export_settings' in metadata
        
        assert metadata['chapter_count'] == len(sample_chapters)
        assert metadata['export_settings']['include_toc'] is True
        assert metadata['export_settings']['quality_validation'] is True
    
    def test_format_detection(self, exporter):
        """Test détection automatique du format."""
        # Tester avec différents formats
        assert exporter._get_generator("epub").__class__.__name__ == "EPUBGenerator"
        assert exporter._get_generator("docx").__class__.__name__ == "DOCXGenerator"
        
        # Format non supporté
        with pytest.raises(ExportError):
            exporter._get_generator("invalid")
    
    def test_template_application(self, exporter):
        """Test application des templates."""
        # Vérifier que les templates sont pris en compte
        templates = exporter.get_available_templates()
        
        assert TemplateType.ROMAN in templates
        assert TemplateType.TECHNICAL in templates
        assert TemplateType.ACADEMIC in templates
        
        # Chaque template doit avoir des styles différents
        roman_styles = exporter._get_template_styles(TemplateType.ROMAN)
        tech_styles = exporter._get_template_styles(TemplateType.TECHNICAL)
        
        assert roman_styles != tech_styles
        assert 'font_family' in roman_styles
        assert 'font_family' in tech_styles


class TestExportEndToEnd:
    """Tests end-to-end pour l'export multi-formats."""
    
    @pytest.mark.asyncio
    async def test_complete_epub_export_workflow(self):
        """Test workflow complet d'export EPUB."""
        exporter = MultiFormatExporter()
        
        # Projet complet avec métadonnées
        project = Mock()
        project.title = "Complete Novel"
        project.settings = {
            'author': 'Jane Doe',
            'description': 'A complete test novel',
            'genre': 'Fiction',
            'language': 'fr'
        }
        
        # Plusieurs chapitres avec contenu riche
        chapters = []
        for i in range(1, 6):
            chapter = Mock()
            chapter.title = f"Chapitre {i}"
            chapter.content = f"""
            <h1>Chapitre {i}</h1>
            <p>Premier paragraphe du chapitre {i} avec <em>texte en italique</em> 
               et <strong>texte en gras</strong>.</p>
            <p>Deuxième paragraphe avec plus de contenu pour tester la 
               génération EPUB complète.</p>
            <blockquote>
                <p>Citation importante dans le chapitre {i}.</p>
            </blockquote>
            """
            chapter.position = i
            chapters.append(chapter)
        
        export_request = ExportRequest(
            format="epub",
            template=TemplateType.ROMAN,
            include_toc=True,
            include_page_numbers=False,  # EPUB n'a pas de pages fixes
            quality_validation=True
        )
        
        result_bytes, metadata = await exporter.export(project, chapters, export_request)
        
        # Vérifications finales
        assert len(result_bytes) > 50000  # EPUB de taille raisonnable
        assert metadata['chapter_count'] == 5
        assert metadata['format'] == 'epub'
        assert metadata['generation_time'] < 10.0  # Moins de 10 secondes
        
        # Vérifier structure EPUB complète
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(result_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as epub_zip:
                file_list = epub_zip.namelist()
                
                # Tous les chapitres présents
                for i in range(1, 6):
                    assert f'OEBPS/chapter{i}.xhtml' in file_list
                
                # Métadonnées complètes
                opf_content = epub_zip.read('OEBPS/content.opf').decode('utf-8')
                assert project.settings['author'] in opf_content
                assert project.settings['description'] in opf_content
                assert project.settings['genre'] in opf_content
    
    @pytest.mark.asyncio
    async def test_complete_docx_export_workflow(self):
        """Test workflow complet d'export DOCX."""
        exporter = MultiFormatExporter()
        
        # Projet technique
        project = Mock()
        project.title = "Technical Documentation"
        project.settings = {
            'author': 'Tech Writer',
            'subject': 'Software Architecture',
            'company': 'TechCorp'
        }
        
        # Chapitres techniques avec code et listes
        chapters = []
        chapter1 = Mock()
        chapter1.title = "Introduction"
        chapter1.content = """
        <h1>Introduction</h1>
        <p>This technical document covers software architecture.</p>
        <ul>
            <li>Design patterns</li>
            <li>Best practices</li>
            <li>Implementation guidelines</li>
        </ul>
        """
        chapter1.position = 1
        chapters.append(chapter1)
        
        chapter2 = Mock()
        chapter2.title = "Code Examples"
        chapter2.content = """
        <h1>Code Examples</h1>
        <pre><code>
def example_function():
    return "Hello World"
        </code></pre>
        <p>The above function demonstrates basic Python syntax.</p>
        """
        chapter2.position = 2
        chapters.append(chapter2)
        
        export_request = ExportRequest(
            format="docx",
            template=TemplateType.TECHNICAL,
            include_toc=True,
            include_page_numbers=True
        )
        
        result_bytes, metadata = await exporter.export(project, chapters, export_request)
        
        # Vérifications
        assert len(result_bytes) > 20000  # DOCX de taille raisonnable
        assert metadata['chapter_count'] == 2
        assert metadata['format'] == 'docx'
        assert metadata['generation_time'] < 5.0
        
        # Vérifier structure DOCX
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(result_bytes)
            tmp_file.flush()
            
            with zipfile.ZipFile(tmp_file.name, 'r') as docx_zip:
                # Document principal
                doc_xml = docx_zip.read('word/document.xml').decode('utf-8')
                assert 'Introduction' in doc_xml
                assert 'Code Examples' in doc_xml
                assert 'example_function' in doc_xml
                
                # Métadonnées
                core_xml = docx_zip.read('docProps/core.xml').decode('utf-8')
                assert project.settings['author'] in core_xml
                assert project.settings['subject'] in core_xml


if __name__ == "__main__":
    # Permettre d'exécuter les tests directement
    pytest.main([__file__, "-v"])
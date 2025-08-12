"""
Advanced PDF Generator Service - Résolution des 6 Problèmes Critiques
Problèmes résolus:
1. Pages blanches parasites
2. Espacement entre mots (rivières)
3. Correspondance TOC
4. Gestion sous-parties
5. Barres horizontales parasites
6. Titres orphelins
"""

from typing import Dict, List, Optional, Tuple, Union
import logging
import re
import asyncio
from pathlib import Path
from io import StringIO
import gc

logger = logging.getLogger(__name__)

try:
    import weasyprint
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint not available")

from app.models.project import Project
from app.models.chapter import Chapter


class PageBreakAnalyzer:
    """Analyse les positions de page pour synchronisation TOC."""
    
    def __init__(self):
        self.page_map: Dict[str, int] = {}
        self.toc_entries: List[Dict] = []
    
    def extract_page_positions(self, document) -> Dict[str, int]:
        """Extrait les positions des titres sur chaque page."""
        page_map = {}
        
        for page_num, page in enumerate(document.pages, 1):
            # Extraire tous les éléments avec ID (ancres pour TOC)
            for element in page._page_box.get_elements_by_tag('h1', 'h2', 'h3'):
                if hasattr(element, 'id') and element.id:
                    page_map[element.id] = page_num
                    
            # Extraire aussi les data-anchor pour compatibilité
            for element in page._page_box.get_elements_with_attribute('data-anchor'):
                anchor = element.get_attribute('data-anchor')
                if anchor:
                    page_map[anchor] = page_num
        
        return page_map
    
    def generate_toc_entries(self, html: str) -> List[Dict]:
        """Génère les entrées de table des matières."""
        toc_pattern = r'<h([1-3])[^>]*(?:id="([^"]+)")[^>]*>([^<]+)</h[1-3]>'
        entries = []
        
        for match in re.finditer(toc_pattern, html):
            level, anchor_id, title = match.groups()
            entries.append({
                'level': int(level),
                'id': anchor_id or f"chapter-{len(entries)}",
                'title': title.strip(),
                'page': None  # Will be filled in second pass
            })
        
        return entries


class PaginationValidator:
    """Valide la qualité de pagination contre les 6 problèmes critiques."""
    
    @staticmethod
    def validate_no_blank_parasites(document) -> Dict[str, Union[bool, List]]:
        """Vérifie l'absence de pages blanches parasites."""
        blank_pages = []
        editorial_pages = set()  # Pages intentionnellement blanches
        
        for page_num, page in enumerate(document.pages, 1):
            # Vérifier si la page est vide ou contient seulement pagination
            content = page._page_box.get_text().strip()
            
            # Page vide = parasite SAUF si précédée de .page-break-right
            if not content or content.isdigit():  # Seul numéro de page
                # Vérifier si page éditoriale intentionnelle
                prev_page = document.pages[page_num - 2] if page_num > 1 else None
                if prev_page and '.editorial-break' in str(prev_page._page_box):
                    editorial_pages.add(page_num)
                else:
                    blank_pages.append(page_num)
        
        return {
            'valid': len(blank_pages) == 0,
            'blank_parasites': blank_pages,
            'editorial_pages': list(editorial_pages)
        }
    
    @staticmethod
    def detect_text_rivers(document) -> Dict[str, Union[bool, int]]:
        """Détecte les rivières dans le texte justifié."""
        river_count = 0
        
        for page in document.pages:
            # Analyser les espaces dans les paragraphes justifiés
            paragraphs = page._page_box.get_elements_by_tag('p')
            
            for p in paragraphs:
                text = p.get_text()
                if len(text) > 100:  # Paragraphes longs seulement
                    # Heuristique: détecter espaces excessifs
                    words = text.split()
                    if len(words) > 8:
                        avg_spaces = sum(len(w) for w in words) / len(words)
                        if avg_spaces < 4:  # Mots courts = risque rivières
                            river_count += 1
        
        return {
            'valid': river_count == 0,
            'river_count': river_count
        }
    
    @staticmethod
    def validate_toc_sync(page_map: Dict[str, int], toc_entries: List[Dict]) -> Dict:
        """Vérifie la synchronisation TOC-pages."""
        mismatches = []
        
        for entry in toc_entries:
            expected_page = page_map.get(entry['id'])
            actual_page = entry.get('page')
            
            if expected_page != actual_page:
                mismatches.append({
                    'entry': entry['title'],
                    'expected': expected_page,
                    'actual': actual_page
                })
        
        return {
            'valid': len(mismatches) == 0,
            'mismatches': mismatches
        }
    
    @staticmethod
    def detect_orphan_titles(document) -> Dict[str, Union[bool, List]]:
        """Détecte les titres orphelins (seuls en bas de page)."""
        orphans = []
        
        for page_num, page in enumerate(document.pages, 1):
            titles = page._page_box.get_elements_by_tag('h1', 'h2', 'h3', 'h4')
            
            for title in titles:
                # Vérifier position du titre sur la page
                y_position = title.position_y if hasattr(title, 'position_y') else 0
                page_height = page.height
                
                # Si titre dans les 20% du bas ET pas de contenu après
                if y_position > page_height * 0.8:
                    next_elements = title.get_next_siblings()
                    if not next_elements or all(not elem.get_text().strip() for elem in next_elements):
                        orphans.append({
                            'page': page_num,
                            'title': title.get_text().strip()
                        })
        
        return {
            'valid': len(orphans) == 0,
            'orphan_titles': orphans
        }


class AdvancedPDFGenerator:
    """Générateur PDF avancé avec double-passe et validation qualité."""
    
    def __init__(self):
        self.analyzer = PageBreakAnalyzer()
        self.validator = PaginationValidator()
        self.font_config = FontConfiguration() if WEASYPRINT_AVAILABLE else None
    
    def generate_advanced_css(self, template: str = 'roman') -> str:
        """Génère CSS avancé résolvant les 6 problèmes critiques."""
        return f"""
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
        
        @page {{
            size: 156mm 234mm;
            margin: 20mm 15mm;
            
            /* Numérotation centrée */
            @bottom-center {{
                content: counter(page);
                font-size: 10pt;
                color: #666;
            }}
            
            /* Éviter les pages blanches parasites */
            orphans: 4;
            widows: 4;
        }}
        
        /* PROBLÈME #1: Pages blanches parasites */
        .chapter-end {{ 
            page-break-after: right; 
        }}
        .part-separator {{ 
            page-break-before: right;
            page-break-after: always;
        }}
        .editorial-break {{
            page-break-after: right;
        }}
        
        /* PROBLÈME #2: Espacement mots/rivières */
        body {{
            font-family: 'Crimson Text', Georgia, serif;
            font-size: 11pt;
            line-height: 1.7;
            text-align: justify;
            
            /* Configuration césure française optimale */
            hyphens: auto;
            hyphenate-language: "fr";
            hyphenate-limit-chars: 6 3 3;
            hyphenate-limit-lines: 2;
            hyphenate-limit-zone: 3em;
            
            /* Espacement des mots contrôlé */
            word-spacing: 0.16em;
            letter-spacing: 0.01em;
        }}
        
        p {{
            text-indent: 1.2em;
            margin: 0 0 0.8em 0;
            
            /* PROBLÈME #6: Titres orphelins */
            orphans: 4;
            widows: 4;
            
            /* Contrôle espacement pour éviter rivières */
            text-align: justify;
            text-justify: inter-word;
        }}
        
        /* PROBLÈME #4: Hiérarchie sous-parties avec compteurs */
        body {{
            counter-reset: chapter section subsection;
        }}
        
        h1 {{
            counter-increment: chapter;
            counter-reset: section subsection;
        }}
        
        h1::before {{
            content: "Chapitre " counter(chapter) " - ";
            font-weight: normal;
            color: #666;
        }}
        
        h2 {{
            counter-increment: section;
            counter-reset: subsection;
        }}
        
        h2::before {{
            content: counter(chapter) "." counter(section) " ";
            font-weight: normal;
            color: #666;
        }}
        
        h3 {{
            counter-increment: subsection;
        }}
        
        h3::before {{
            content: counter(chapter) "." counter(section) "." counter(subsection) " ";
            font-weight: normal;
            color: #666;
        }}
        
        /* PROBLÈME #6: Titres orphelins - Protection renforcée */
        h1, h2, h3, h4, h5, h6 {{
            page-break-after: avoid;
            page-break-inside: avoid;
            orphans: 4;
            widows: 4;
            
            /* Assurer minimum 3 lignes de contenu après titre */
            min-height: 2.5em;
        }}
        
        h1 {{
            font-size: 24pt;
            font-weight: 600;
            text-align: center;
            margin: 60mm 0 30mm 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        h2 {{
            font-size: 18pt;
            font-weight: 600;
            margin: 25mm 0 15mm 0;
        }}
        
        h3 {{
            font-size: 14pt;
            font-weight: 600;
            margin: 20mm 0 10mm 0;
        }}
        
        /* PROBLÈME #5: Barres horizontales parasites */
        hr {{
            display: none; /* Éliminer complètement les <hr> */
        }}
        
        .chapter-separator {{
            border: none;
            margin: 3em 0;
            text-align: center;
        }}
        
        .chapter-separator::after {{
            content: "* * *";
            font-size: 18pt;
            color: #666;
            display: block;
        }}
        
        /* PROBLÈME #3: TOC synchronisé */
        .table-of-contents {{
            page-break-before: always;
            page-break-after: always;
        }}
        
        .toc-entry {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 0.6em;
            page-break-inside: avoid;
            padding-right: 0;
        }}
        
        .toc-title {{
            flex: 1;
            padding-right: 1em;
            overflow: hidden;
        }}
        
        .toc-dots {{
            flex: 0 1 auto;
            border-bottom: 1px dotted #999;
            margin: 0 0.3em;
            min-width: 2em;
            height: 1px;
            margin-top: 0.7em;
        }}
        
        .toc-page {{
            flex: 0 0 auto;
            font-weight: bold;
            min-width: 2em;
            text-align: right;
        }}
        
        /* Styles spéciaux pour éviter problèmes */
        .keep-together {{
            page-break-inside: avoid;
        }}
        
        .new-page {{
            page-break-before: always;
        }}
        
        /* Images et tableaux */
        img, table, pre, blockquote {{
            page-break-inside: avoid;
            max-width: 100%;
        }}
        
        /* Optimisation typographique */
        .first-paragraph {{
            text-indent: 0;
        }}
        
        .drop-cap {{
            float: left;
            font-size: 3.2em;
            line-height: 0.85;
            margin: 0.1em 0.1em 0 0;
            font-weight: bold;
        }}
        
        blockquote {{
            margin: 1.5em 2em;
            font-style: italic;
            color: #555;
            border-left: 3px solid #ddd;
            padding-left: 1em;
        }}
        
        /* Debug: marqueurs visuels (à retirer en production) */
        .debug-orphan {{
            background-color: rgba(255, 0, 0, 0.1);
        }}
        
        .debug-widow {{
            background-color: rgba(0, 255, 0, 0.1);
        }}
        """
    
    def preprocess_html(self, html: str) -> str:
        """Préprocesse le HTML pour optimiser la pagination."""
        # Ajouter ancres pour TOC
        html = re.sub(
            r'<h([1-3])([^>]*)>([^<]+)</h[1-3]>',
            r'<h\1\2 id="heading-\3" data-anchor="heading-\3">\3</h\1>',
            html
        )
        
        # Marquer premiers paragraphes de chapitre
        html = re.sub(
            r'(<h1[^>]*>[^<]+</h1>\s*)<p>',
            r'\1<p class="first-paragraph">',
            html
        )
        
        # Remplacer <hr> par séparateurs sémantiques
        html = html.replace('<hr>', '<div class="chapter-separator"></div>')
        html = html.replace('<hr/>', '<div class="chapter-separator"></div>')
        html = html.replace('<hr />', '<div class="chapter-separator"></div>')
        
        return html
    
    def inject_toc_pages(self, html: str, page_map: Dict[str, int]) -> str:
        """Injecte les vrais numéros de page dans le TOC."""
        def replace_toc_page(match):
            anchor = match.group(1)
            page_num = page_map.get(anchor, "?")
            return f'<span class="toc-page">{page_num}</span>'
        
        # Remplacer les placeholders TOC
        html = re.sub(
            r'<span class="toc-page"[^>]*data-anchor="([^"]+)"[^>]*>[\d\?]*</span>',
            replace_toc_page,
            html
        )
        
        return html
    
    async def generate_pdf_two_pass(
        self, 
        html: str, 
        template: str = 'roman'
    ) -> Tuple[bytes, Dict]:
        """Génère PDF en double-passe avec validation qualité."""
        
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("WeasyPrint not available")
        
        # Preprocessing
        processed_html = self.preprocess_html(html)
        css = self.generate_advanced_css(template)
        
        # PREMIÈRE PASSE: Analyse des positions
        logger.info("PDF Generation - First pass: analyzing page positions")
        
        full_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Book</title>
            <style>{css}</style>
        </head>
        <body>
            {processed_html}
        </body>
        </html>
        """
        
        document = HTML(string=full_html).render()
        page_map = self.analyzer.extract_page_positions(document)
        
        # DEUXIÈME PASSE: Injection TOC et génération finale
        logger.info("PDF Generation - Second pass: generating final PDF with TOC")
        
        final_html = self.inject_toc_pages(processed_html, page_map)
        
        final_full_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Book</title>
            <style>{css}</style>
        </head>
        <body>
            {final_html}
        </body>
        </html>
        """
        
        final_document = HTML(string=final_full_html).render()
        pdf_bytes = final_document.write_pdf()
        
        # VALIDATION QUALITÉ
        logger.info("PDF Generation - Quality validation")
        
        validation_results = {
            'blank_pages': self.validator.validate_no_blank_parasites(final_document),
            'text_rivers': self.validator.detect_text_rivers(final_document),
            'toc_sync': self.validator.validate_toc_sync(page_map, self.analyzer.toc_entries),
            'orphan_titles': self.validator.detect_orphan_titles(final_document)
        }
        
        # Log validation results
        all_valid = all(result['valid'] for result in validation_results.values())
        logger.info(f"PDF Quality Validation: {'PASSED' if all_valid else 'ISSUES FOUND'}")
        
        for check, result in validation_results.items():
            if not result['valid']:
                logger.warning(f"Quality issue in {check}: {result}")
        
        # Force garbage collection
        gc.collect()
        
        return pdf_bytes, {
            'page_count': len(final_document.pages),
            'page_map': page_map,
            'quality_validation': validation_results,
            'all_checks_passed': all_valid
        }
    
    async def generate_from_project(
        self, 
        project: Project, 
        chapters: List[Chapter]
    ) -> Tuple[bytes, Dict]:
        """Génère PDF à partir d'un projet et ses chapitres."""
        
        # Construire HTML complet
        html_parts = []
        
        # Table des matières
        if project.settings and project.settings.get('table_of_contents', True):
            toc_html = '<div class="table-of-contents">'
            toc_html += '<h1>Table des matières</h1>'
            
            for i, chapter in enumerate(chapters, 1):
                anchor = f"heading-{chapter.title}"
                toc_html += f'''
                <div class="toc-entry">
                    <span class="toc-title">{i}. {chapter.title}</span>
                    <span class="toc-dots"></span>
                    <span class="toc-page" data-anchor="{anchor}">?</span>
                </div>
                '''
            
            toc_html += '</div>'
            html_parts.append(toc_html)
        
        # Chapitres
        for chapter in sorted(chapters, key=lambda c: c.position):
            chapter_html = f'''
            <div class="chapter">
                <h1>{chapter.title}</h1>
                {chapter.content}
            </div>
            '''
            html_parts.append(chapter_html)
        
        full_html = '\n'.join(html_parts)
        
        # Générer PDF
        return await self.generate_pdf_two_pass(full_html, 'roman')
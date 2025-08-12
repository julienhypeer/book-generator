"""
Tests TDD pour le système de templates CSS avancés.
Tests écrits d'abord selon l'approche TDD pour PR #11.
"""

import pytest
from unittest.mock import Mock, patch
import re
from typing import Dict, List, Any

# Import du service à implémenter
from app.services.advanced_css_templates import (
    CSSTemplateManager,
    TemplateRenderer,
    CSSValidator,
    TemplateError,
)
from app.validators.export import TemplateType


class TestCSSTemplateManager:
    """Tests TDD pour le gestionnaire de templates CSS."""

    @pytest.fixture
    def template_manager(self):
        return CSSTemplateManager()

    def test_get_available_templates(self, template_manager):
        """Test récupération des templates disponibles."""
        templates = template_manager.get_available_templates()

        assert isinstance(templates, list)
        assert TemplateType.ROMAN in templates
        assert TemplateType.TECHNICAL in templates
        assert TemplateType.ACADEMIC in templates
        assert len(templates) >= 3

    def test_get_template_config_roman(self, template_manager):
        """Test configuration template roman."""
        config = template_manager.get_template_config(TemplateType.ROMAN)

        # Vérifier structure config
        assert "name" in config
        assert "description" in config
        assert "typography" in config
        assert "layout" in config
        assert "colors" in config

        # Vérifier spécificités roman
        assert (
            config["typography"]["font_family"]
            == "Crimson Text, Georgia, serif"
        )
        assert config["typography"]["text_align"] == "justify"
        assert "serif" in config["typography"]["font_family"]

        # Vérifier marges livre
        assert config["layout"]["page_size"] == "156mm 234mm"
        assert config["layout"]["margins"]["top"] == "20mm"

    def test_get_template_config_technical(self, template_manager):
        """Test configuration template technique."""
        config = template_manager.get_template_config(TemplateType.TECHNICAL)

        # Vérifier spécificités techniques
        assert "sans-serif" in config["typography"]["font_family"]
        assert config["typography"]["line_height"] <= 1.5  # Plus serré
        assert config["layout"]["code_blocks"] is True
        assert "syntax_highlighting" in config["features"]

    def test_get_template_config_academic(self, template_manager):
        """Test configuration template académique."""
        config = template_manager.get_template_config(TemplateType.ACADEMIC)

        # Vérifier spécificités académiques
        assert "Times" in config["typography"]["font_family"]
        assert config["typography"]["line_height"] >= 1.8  # Double interligne
        assert config["layout"]["footnotes"] is True
        assert config["features"]["bibliography"] is True

    def test_invalid_template_error(self, template_manager):
        """Test erreur pour template invalide."""
        with pytest.raises(TemplateError) as exc_info:
            template_manager.get_template_config("invalid_template")

        assert "Unknown template" in str(exc_info.value)

    def test_template_inheritance(self, template_manager):
        """Test héritage des templates depuis base."""
        base_config = template_manager.get_base_config()
        roman_config = template_manager.get_template_config(TemplateType.ROMAN)

        # Vérifier que base est inclus
        assert (
            base_config["quality_rules"]["orphans"]
            == roman_config["quality_rules"]["orphans"]
        )
        assert (
            base_config["quality_rules"]["widows"]
            == roman_config["quality_rules"]["widows"]
        )

        # Mais avec spécificités roman
        assert (
            roman_config["typography"]["font_family"]
            != base_config["typography"]["font_family"]
        )


class TestTemplateRenderer:
    """Tests TDD pour le moteur de rendu CSS."""

    @pytest.fixture
    def renderer(self):
        return TemplateRenderer()

    @pytest.fixture
    def sample_config(self):
        return {
            "name": "Test Template",
            "typography": {
                "font_family": "Test Font, serif",
                "font_size": "12pt",
                "line_height": "1.6",
            },
            "layout": {
                "page_size": "156mm 234mm",
                "margins": {
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm",
                },
            },
            "quality_rules": {
                "orphans": 4,
                "widows": 4,
                "avoid_page_breaks": ["h1", "h2", "h3"],
            },
        }

    def test_render_base_css_structure(self, renderer, sample_config):
        """Test génération CSS de base."""
        css = renderer.render_template_css(sample_config)

        # Vérifier structure CSS
        assert isinstance(css, str)
        assert "@page {" in css
        assert "body {" in css
        assert len(css) > 1000  # CSS substantiel

    def test_render_typography_rules(self, renderer, sample_config):
        """Test génération règles typographiques."""
        css = renderer.render_template_css(sample_config)

        # Vérifier typography
        assert "font-family: Test Font, serif" in css
        assert "font-size: 12pt" in css
        assert "line-height: 1.6" in css

    def test_render_page_layout(self, renderer, sample_config):
        """Test génération layout de page."""
        css = renderer.render_template_css(sample_config)

        # Vérifier @page
        assert "size: 156mm 234mm" in css
        assert "margin: 20mm 15mm" in css

    def test_render_quality_rules(self, renderer, sample_config):
        """Test génération règles qualité."""
        css = renderer.render_template_css(sample_config)

        # Vérifier orphans/widows
        assert "orphans: 4" in css
        assert "widows: 4" in css

        # Vérifier page-breaks
        assert "h1, h2, h3 {" in css or "page-break-after: avoid" in css

    def test_render_with_custom_variables(self, renderer, sample_config):
        """Test rendu avec variables CSS."""
        variables = {
            "primary_color": "#2c3e50",
            "accent_color": "#3498db",
            "code_font": "Fira Code, monospace",
        }

        css = renderer.render_template_css(sample_config, variables=variables)

        # Vérifier variables CSS
        assert "--primary-color: #2c3e50" in css
        assert "--accent-color: #3498db" in css

    def test_render_responsive_features(self, renderer, sample_config):
        """Test rendu fonctionnalités responsives."""
        css = renderer.render_template_css(sample_config)

        # Vérifier media queries pour différents formats
        assert "@media print" in css
        # Vérifier viewport adaptation pour preview
        assert "max-width: 100%" in css

    def test_critical_pagination_rules_included(self, renderer, sample_config):
        """Test inclusion des 6 règles critiques de pagination."""
        css = renderer.render_template_css(sample_config)

        # PROBLÈME #1: Pages blanches parasites
        assert (
            "page-break-after: right" in css
            or "page-break-before: right" in css
        )

        # PROBLÈME #2: Césure française
        assert "hyphens: auto" in css
        assert 'hyphenate-language: "fr"' in css

        # PROBLÈME #5: Barres horizontales
        assert "hr {" in css and "display: none" in css

        # PROBLÈME #6: Titres orphelins
        assert "page-break-after: avoid" in css

    def test_render_with_invalid_config(self, renderer):
        """Test gestion configuration invalide."""
        invalid_config = {"invalid": "config"}

        with pytest.raises(TemplateError):
            renderer.render_template_css(invalid_config)


class TestCSSValidator:
    """Tests TDD pour le validateur CSS."""

    @pytest.fixture
    def validator(self):
        return CSSValidator()

    def test_validate_complete_css(self, validator):
        """Test validation CSS complet."""
        valid_css = """
        @page { size: 156mm 234mm; margin: 20mm 15mm; }
        body { font-family: serif; hyphens: auto; }
        h1, h2, h3 { page-break-after: avoid; orphans: 4; widows: 4; }
        hr { display: none; }
        """

        result = validator.validate_css(valid_css)

        assert result["valid"] is True
        assert result["score"] >= 85  # Score élevé pour CSS complet
        # Vérifier qu'il n'y a que des warnings, pas d'erreurs critiques
        critical_issues = [
            i for i in result["issues"] if i["severity"] == "critical"
        ]
        assert len(critical_issues) == 0

    def test_validate_missing_critical_rules(self, validator):
        """Test détection règles critiques manquantes."""
        incomplete_css = """
        body { font-family: serif; }
        """

        result = validator.validate_css(incomplete_css)

        assert result["valid"] is False
        assert result["score"] < 50
        assert len(result["issues"]) > 0

        # Vérifier détection problèmes spécifiques
        issues = [issue["type"] for issue in result["issues"]]
        assert "missing_page_rules" in issues
        assert "missing_hyphenation" in issues

    def test_validate_pagination_quality(self, validator):
        """Test validation qualité pagination."""
        css_with_pagination = """
        @page { size: A4; margin: 2cm; }
        h1, h2 { page-break-after: avoid; orphans: 4; widows: 4; }
        """

        result = validator.validate_pagination_quality(css_with_pagination)

        assert "orphans_protection" in result
        assert "widows_protection" in result
        assert "title_protection" in result

        assert result["orphans_protection"] is True
        assert result["widows_protection"] is True

    def test_validate_typography_quality(self, validator):
        """Test validation qualité typographique."""
        css_typography = """
        body { 
            font-family: "Crimson Text", serif;
            font-size: 11pt;
            line-height: 1.6;
            hyphens: auto;
            hyphenate-language: "fr";
        }
        """

        result = validator.validate_typography_quality(css_typography)

        assert "font_quality" in result
        assert "hyphenation_setup" in result
        assert "line_height_optimal" in result

        assert result["hyphenation_setup"] is True
        assert result["font_quality"] >= 0.8  # Score qualité police

    def test_generate_quality_report(self, validator):
        """Test génération rapport qualité."""
        test_css = """
        @page { size: 156mm 234mm; }
        body { font-family: serif; hyphens: auto; }
        """

        report = validator.generate_quality_report(test_css)

        # Vérifier structure rapport
        assert "overall_score" in report
        assert "categories" in report
        assert "recommendations" in report
        assert "critical_issues" in report

        # Vérifier catégories évaluées
        categories = report["categories"]
        assert "pagination" in categories
        assert "typography" in categories
        assert "layout" in categories

    def test_performance_validation(self, validator):
        """Test validation performance CSS."""
        heavy_css = (
            """
        * { transition: all 0.3s ease; }
        body { box-shadow: 0 0 100px rgba(0,0,0,0.5); }
        """
            + "div { margin: 1px; }\n" * 1000
        )  # CSS très lourd

        result = validator.validate_performance(heavy_css)

        assert "size_warning" in result
        assert "complexity_score" in result
        assert result["complexity_score"] > 0.7  # CSS complexe détecté


class TestAdvancedCSSIntegration:
    """Tests d'intégration du système de templates CSS."""

    def test_complete_template_workflow(self):
        """Test workflow complet: config -> CSS -> validation."""
        manager = CSSTemplateManager()
        renderer = TemplateRenderer()
        validator = CSSValidator()

        # 1. Récupérer config template
        config = manager.get_template_config(TemplateType.ROMAN)
        assert config is not None

        # 2. Générer CSS
        css = renderer.render_template_css(config)
        assert len(css) > 0

        # 3. Valider qualité
        validation = validator.validate_css(css)
        assert validation["valid"] is True
        assert validation["score"] >= 80

    def test_template_comparison(self):
        """Test différences entre templates."""
        manager = CSSTemplateManager()
        renderer = TemplateRenderer()

        # Générer CSS pour chaque template
        roman_css = renderer.render_template_css(
            manager.get_template_config(TemplateType.ROMAN)
        )
        technical_css = renderer.render_template_css(
            manager.get_template_config(TemplateType.TECHNICAL)
        )

        # Vérifier différences
        assert roman_css != technical_css
        assert "serif" in roman_css
        assert "sans-serif" in technical_css

        # Mais règles communes présentes
        for css in [roman_css, technical_css]:
            assert "@page {" in css
            assert "hyphens: auto" in css
            assert "orphans:" in css

    def test_css_minification(self):
        """Test minification CSS pour production."""
        manager = CSSTemplateManager()
        renderer = TemplateRenderer()

        config = manager.get_template_config(TemplateType.ROMAN)

        # CSS normal
        css_normal = renderer.render_template_css(config, minify=False)

        # CSS minifié
        css_minified = renderer.render_template_css(config, minify=True)

        # Vérifier minification
        assert len(css_minified) < len(css_normal)
        assert "\n" not in css_minified or css_minified.count(
            "\n"
        ) < css_normal.count("\n")

        # Mais contenu identique
        assert "font-family" in css_minified
        assert "@page" in css_minified

    def test_custom_theme_variables(self):
        """Test application variables de thème personnalisé."""
        renderer = TemplateRenderer()

        base_config = {
            "typography": {"font_family": "serif"},
            "layout": {"page_size": "A4"},
            "quality_rules": {"orphans": 4},
        }

        custom_vars = {
            "brand_color": "#ff6b35",
            "heading_color": "#2c3e50",
            "link_color": "#3498db",
        }

        css = renderer.render_template_css(base_config, variables=custom_vars)

        # Vérifier variables appliquées
        assert "--brand-color: #ff6b35" in css
        assert "color: var(--heading-color)" in css or "#2c3e50" in css

    def test_error_handling_chain(self):
        """Test gestion erreurs dans la chaîne complète."""
        manager = CSSTemplateManager()
        renderer = TemplateRenderer()

        # Template inexistant
        with pytest.raises(TemplateError):
            manager.get_template_config("nonexistent")

        # Config invalide pour renderer
        with pytest.raises(TemplateError):
            renderer.render_template_css({})

    @pytest.mark.asyncio
    async def test_async_css_generation(self):
        """Test génération CSS asynchrone pour gros projets."""
        manager = CSSTemplateManager()
        renderer = TemplateRenderer()

        # Simuler génération async
        configs = [
            manager.get_template_config(TemplateType.ROMAN),
            manager.get_template_config(TemplateType.TECHNICAL),
            manager.get_template_config(TemplateType.ACADEMIC),
        ]

        # Générer CSS en parallèle (simulation)
        css_results = []
        for config in configs:
            css = renderer.render_template_css(config)
            css_results.append(css)

        assert len(css_results) == 3
        assert all(len(css) > 1000 for css in css_results)


if __name__ == "__main__":
    # Permettre d'exécuter les tests directement
    pytest.main([__file__, "-v"])

"""
Service de templates CSS avancés pour génération PDF professionnelle.
Implémentation élégante et directe selon tests TDD.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

from app.validators.export import TemplateType  # noqa: E402


class TemplateError(Exception):
    """Exception pour les erreurs de template CSS."""

    pass


class CSSTemplateManager:
    """Gestionnaire des configurations de templates CSS."""

    def __init__(self):
        self._templates_config = self._init_templates_config()
        self._base_config = self._init_base_config()

    def get_available_templates(self) -> List[TemplateType]:
        """Retourne la liste des templates disponibles."""
        return [
            TemplateType.ROMAN,
            TemplateType.TECHNICAL,
            TemplateType.ACADEMIC,
        ]

    def get_template_config(
        self, template: Union[str, TemplateType]
    ) -> Dict[str, Any]:
        """Récupère la configuration d'un template."""
        if isinstance(template, str):
            template_key = template
        else:
            template_key = template.value

        if template_key not in self._templates_config:
            raise TemplateError(f"Unknown template: {template_key}")

        # Fusionner avec base config
        base = self._base_config.copy()
        template_specific = self._templates_config[template_key].copy()

        # Merge récursif
        return self._deep_merge(base, template_specific)

    def get_base_config(self) -> Dict[str, Any]:
        """Retourne la configuration de base."""
        return self._base_config.copy()

    def _init_base_config(self) -> Dict[str, Any]:
        """Configuration de base commune à tous les templates."""
        return {
            "name": "Base Template",
            "description": "Configuration de base pour tous les templates",
            "layout": {
                "page_size": "156mm 234mm",
                "margins": {
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm",
                },
                "footnotes": False,
                "code_blocks": False,
            },
            "quality_rules": {
                "orphans": 4,
                "widows": 4,
                "avoid_page_breaks": ["h1", "h2", "h3", "h4"],
                "hyphenation": {
                    "enabled": True,
                    "language": "fr",
                    "min_chars": 6,
                    "min_left": 3,
                    "min_right": 3,
                },
            },
            "typography": {
                "font_family": "serif",
                "font_size": "12pt",
                "line_height": "1.6",
                "text_align": "left",
            },
            "colors": {
                "text": "#2c3e50",
                "headings": "#34495e",
                "accent": "#3498db",
                "muted": "#7f8c8d",
            },
            "features": {
                "table_of_contents": True,
                "page_numbers": True,
                "headers_footers": True,
                "syntax_highlighting": False,
                "bibliography": False,
            },
        }

    def _init_templates_config(self) -> Dict[str, Dict[str, Any]]:
        """Configuration spécifique de chaque template."""
        return {
            "roman": {
                "name": "Roman Template",
                "description": "Template élégant pour romans et littérature",
                "typography": {
                    "font_family": "Crimson Text, Georgia, serif",
                    "font_size": "11pt",
                    "line_height": "1.7",
                    "text_align": "justify",
                    "text_indent": "1.2em",
                    "paragraph_spacing": "0.8em",
                },
                "headings": {
                    "h1": {
                        "font_size": "24pt",
                        "font_weight": "600",
                        "text_transform": "uppercase",
                        "text_align": "center",
                        "margin_top": "60mm",
                        "margin_bottom": "30mm",
                        "letter_spacing": "2px",
                    },
                    "h2": {
                        "font_size": "18pt",
                        "font_weight": "600",
                        "margin_top": "25mm",
                        "margin_bottom": "15mm",
                    },
                },
                "colors": {
                    "text": "#2c3e50",
                    "headings": "#2c3e50",
                    "accent": "#8e44ad",
                },
            },
            "technical": {
                "name": "Technical Template",
                "description": "Template moderne pour documentation technique",
                "typography": {
                    "font_family": "Source Sans Pro, Arial, sans-serif",
                    "font_size": "10.5pt",
                    "line_height": 1.4,
                    "text_align": "left",
                    "text_indent": "0",
                    "paragraph_spacing": "0.6em",
                },
                "headings": {
                    "h1": {
                        "font_size": "20pt",
                        "font_weight": "700",
                        "text_transform": "none",
                        "text_align": "left",
                        "margin_top": "40mm",
                        "margin_bottom": "20mm",
                        "border_bottom": "2px solid #3498db",
                    },
                    "h2": {
                        "font_size": "16pt",
                        "font_weight": "600",
                        "margin_top": "20mm",
                        "margin_bottom": "10mm",
                        "color": "#2980b9",
                    },
                },
                "layout": {
                    "code_blocks": True,
                    "margins": {
                        "top": "18mm",
                        "bottom": "18mm",
                        "left": "12mm",
                        "right": "12mm",
                    },
                },
                "colors": {
                    "text": "#2c3e50",
                    "headings": "#2980b9",
                    "accent": "#3498db",
                    "code_bg": "#f8f9fa",
                    "code_border": "#dee2e6",
                },
                "features": {
                    "syntax_highlighting": True,
                    "code_line_numbers": True,
                },
            },
            "academic": {
                "name": "Academic Template",
                "description": "Template formel pour publications académiques",
                "typography": {
                    "font_family": "Times New Roman, serif",
                    "font_size": "12pt",
                    "line_height": 2.0,
                    "text_align": "justify",
                    "text_indent": "0.5in",
                    "paragraph_spacing": "0",
                },
                "headings": {
                    "h1": {
                        "font_size": "16pt",
                        "font_weight": "bold",
                        "text_transform": "none",
                        "text_align": "center",
                        "margin_top": "24pt",
                        "margin_bottom": "12pt",
                    },
                    "h2": {
                        "font_size": "14pt",
                        "font_weight": "bold",
                        "margin_top": "18pt",
                        "margin_bottom": "6pt",
                    },
                },
                "layout": {
                    "footnotes": True,
                    "margins": {
                        "top": "25mm",
                        "bottom": "25mm",
                        "left": "25mm",
                        "right": "25mm",
                    },
                },
                "colors": {
                    "text": "#000000",
                    "headings": "#000000",
                    "accent": "#000000",
                },
                "features": {
                    "bibliography": True,
                    "footnotes": True,
                    "line_numbers": False,
                },
            },
        }

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Fusion récursive de dictionnaires."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result


class TemplateRenderer:
    """Moteur de rendu CSS à partir des configurations."""

    def __init__(self):
        self._css_modules = {
            "base": self._render_base_css,
            "typography": self._render_typography_css,
            "layout": self._render_layout_css,
            "quality": self._render_quality_css,
            "headings": self._render_headings_css,
            "colors": self._render_colors_css,
            "features": self._render_features_css,
        }

    def render_template_css(
        self,
        config: Dict[str, Any],
        variables: Optional[Dict[str, str]] = None,
        minify: bool = False,
    ) -> str:
        """Génère le CSS complet à partir de la configuration."""
        if not config or not isinstance(config, dict):
            raise TemplateError("Invalid configuration provided")

        # Valider que config contient au moins les sections de base
        required_sections = ["layout", "quality_rules"]
        missing_sections = [
            section for section in required_sections if section not in config
        ]
        if missing_sections:
            raise TemplateError(
                f"Missing required configuration sections: {missing_sections}"
            )

        css_parts = []

        # CSS Variables
        if variables:
            css_parts.append(self._render_css_variables(variables))

        # Modules CSS - TOUJOURS rendre tous les modules critiques
        for module_name, renderer_func in self._css_modules.items():
            try:
                module_css = renderer_func(config)
                if module_css:
                    css_parts.append(f"/* {module_name.title()} */")
                    css_parts.append(module_css)
            except Exception as e:
                logger.warning(f"Error rendering {module_name}: {e}")

        # Assembler CSS
        full_css = "\n\n".join(css_parts)

        # Minification si demandée
        if minify:
            full_css = self._minify_css(full_css)

        return full_css

    def _render_base_css(self, config: Dict) -> str:
        """Génère les règles CSS de base."""
        page_size = config.get("layout", {}).get("page_size", "156mm 234mm")
        margins = config.get("layout", {}).get("margins", {})
        margin_str = (
            f"{margins.get('top', '20mm')} "
            f"{margins.get('right', '15mm')} "
            f"{margins.get('bottom', '20mm')} "
            f"{margins.get('left', '15mm')}"
        )

        return f"""
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');

@page {{
    size: {page_size};
    margin: {margin_str};

    @bottom-center {{
        content: counter(page);
        font-size: 10pt;
        color: #666;
    }}

    orphans: {config.get('quality_rules', {}).get('orphans', 4)};
    widows: {config.get('quality_rules', {}).get('widows', 4)};
}}

* {{
    box-sizing: border-box;
}}

html, body {{
    margin: 0;
    padding: 0;
}}
"""

    def _render_typography_css(self, config: Dict) -> str:
        """Génère les règles typographiques."""
        typo = config.get("typography", {})
        quality_rules = config.get("quality_rules", {})
        hyphenation = quality_rules.get("hyphenation", {})

        return f"""
body {{
    font-family: {typo.get('font_family', 'serif')};
    font-size: {typo.get('font_size', '12pt')};
    line-height: {typo.get('line_height', '1.6')};
    text-align: {typo.get('text_align', 'left')};
    color: {config.get('colors', {}).get('text', '#2c3e50')};

    /* Césure française pour éviter les rivières */
    {f'hyphens: auto;' if hyphenation.get('enabled', True) else ''}
    {f'hyphenate-language: "{hyphenation.get("language", "fr")}";' if hyphenation.get('enabled', True) else ''}
    {f'hyphenate-limit-chars: {hyphenation.get("min_chars", 6)} '
      f'{hyphenation.get("min_left", 3)} {hyphenation.get("min_right", 3)};'
      if hyphenation.get('enabled', True) else ''}
    hyphenate-limit-lines: 2;
    hyphenate-limit-zone: 3em;

    /* Contrôle espacement mots */
    word-spacing: 0.16em;
    letter-spacing: 0.01em;
}}

p {{
    text-indent: {typo.get('text_indent', '0')};
    margin: 0 0 {typo.get('paragraph_spacing', '1em')} 0;
    text-align: {typo.get('text_align', 'left')};
    text-justify: inter-word;

    /* Protection orphelins/veuves */
    orphans: {quality_rules.get('orphans', 4)};
    widows: {quality_rules.get('widows', 4)};
}}

.first-paragraph {{
    text-indent: 0;
}}
"""

    def _render_layout_css(self, config: Dict) -> str:
        """Génère les règles de layout."""
        layout = config.get("layout", {})

        css = """
/* Images et éléments de contenu */
img, table, pre, blockquote {
    page-break-inside: avoid;
    max-width: 100%;
}

blockquote {
    margin: 1.5em 2em;
    font-style: italic;
    color: #555;
    border-left: 3px solid #ddd;
    padding-left: 1em;
}

.keep-together {
    page-break-inside: avoid;
}

.new-page {
    page-break-before: always;
}

/* Protection contre pages blanches parasites */
.chapter-end {
    page-break-after: right;
}

.part-separator {
    page-break-before: right;
    page-break-after: always;
}

.editorial-break {
    page-break-after: right;
}
"""

        # Code blocks pour templates techniques
        if layout.get("code_blocks", False):
            css += """
pre, code {
    font-family: 'Fira Code', 'Courier New', monospace;
    background-color: var(--code-bg, #f8f9fa);
    border: 1px solid var(--code-border, #dee2e6);
}

pre {
    padding: 1em;
    margin: 1em 0;
    page-break-inside: avoid;
    overflow-x: auto;
}

code {
    padding: 0.2em 0.4em;
    font-size: 0.9em;
}
"""

        return css

    def _render_quality_css(self, config: Dict) -> str:
        """Génère les règles de qualité (6 problèmes critiques)."""
        avoid_breaks = config.get("quality_rules", {}).get(
            "avoid_page_breaks", ["h1", "h2", "h3"]
        )

        return f"""
/* PROBLÈME #6: Titres orphelins - Protection renforcée */
{', '.join(avoid_breaks)} {{
    page-break-after: avoid;
    page-break-inside: avoid;
    orphans: 4;
    widows: 4;
    min-height: 2.5em;
}}

/* PROBLÈME #5: Barres horizontales parasites - Élimination */
hr {{
    display: none;
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

/* Responsive pour preview */
@media screen {{
    body {{
        max-width: 800px;
        margin: 0 auto;
        padding: 2em;
        background: white;
    }}
}}

@media print {{
    body {{
        background: white;
    }}

    /* Éviter barres parasites en impression */
    hr {{
        display: none;
    }}
}}
"""

    def _render_headings_css(self, config: Dict) -> str:
        """Génère les règles pour les titres."""
        headings = config.get("headings", {})
        colors = config.get("colors", {})

        css = """
/* Hiérarchie avec compteurs */
body {{
    counter-reset: chapter section subsection;
}}

h1 {{
    counter-increment: chapter;
    counter-reset: section subsection;
}}

h2 {{
    counter-increment: section;
    counter-reset: subsection;
}}

h3 {{
    counter-increment: subsection;
}}
"""

        # Styles spécifiques pour chaque niveau
        for level in ["h1", "h2", "h3", "h4"]:
            if level in headings:
                styles = headings[level]
                css += f"""
{level} {{
    font-size: {styles.get('font_size', '1.2em')};
    font-weight: {styles.get('font_weight', 'bold')};
    color: {styles.get('color', colors.get('headings', '#2c3e50'))};
    text-align: {styles.get('text_align', 'left')};
    margin: {styles.get('margin_top', '1em')} 0 
            {styles.get('margin_bottom', '0.5em')} 0;
    {f"text-transform: {styles['text_transform']};" if 'text_transform' in styles else ""}
    {f"letter-spacing: {styles['letter_spacing']};" if 'letter_spacing' in styles else ""}
    {f"border-bottom: {styles['border_bottom']};" if 'border_bottom' in styles else ""}
}}
"""

        return css

    def _render_colors_css(self, config: Dict) -> str:
        """Génère les règles de couleurs."""
        colors = config.get("colors", {})

        if not colors:
            return ""

        return f"""
/* Palette de couleurs */
a {{
    color: {colors.get('accent', '#3498db')};
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

.muted {{
    color: {colors.get('muted', '#7f8c8d')};
}}

.accent {{
    color: {colors.get('accent', '#3498db')};
}}
"""

    def _render_features_css(self, config: Dict) -> str:
        """Génère CSS pour les fonctionnalités spéciales."""
        features = config.get("features", {})
        css = ""

        if features.get("footnotes", False):
            css += """
.footnote {
    font-size: 0.85em;
    margin-top: 2em;
    border-top: 1px solid #ccc;
    padding-top: 0.5em;
}

.footnote-ref {
    vertical-align: super;
    font-size: 0.7em;
}
"""

        if features.get("syntax_highlighting", False):
            css += """
.highlight {
    background-color: #f8f9fa;
    padding: 1em;
    border-radius: 4px;
    page-break-inside: avoid;
}

.keyword { color: #d73a49; font-weight: bold; }
.string { color: #032f62; }
.comment { color: #6a737d; font-style: italic; }
.number { color: #005cc5; }
"""

        return css

    def _render_css_variables(self, variables: Dict[str, str]) -> str:
        """Génère les variables CSS personnalisées."""
        css_vars = []

        for key, value in variables.items():
            css_var_name = key.replace("_", "-")
            css_vars.append(f"    --{css_var_name}: {value};")

        return f"""
:root {{
{chr(10).join(css_vars)}
}}
"""

    def _minify_css(self, css: str) -> str:
        """Minifie le CSS pour la production."""
        # Supprimer commentaires
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)

        # Supprimer espaces multiples
        css = re.sub(r"\s+", " ", css)

        # Supprimer espaces autour des signes
        css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)

        # Supprimer point-virgule avant accolade fermante
        css = re.sub(r";}", "}", css)

        return css.strip()


class CSSValidator:
    """Validateur de qualité CSS pour templates."""

    def __init__(self):
        self.critical_rules = {
            "page_rules": r"@page\s*\{",
            "hyphenation": r"hyphens:\s*auto",
            "orphans": r"orphans:\s*\d+",
            "widows": r"widows:\s*\d+",
            "avoid_breaks": r"page-break-after:\s*avoid",
            "hr_hidden": r"hr\s*\{.*?display:\s*none",
        }

    def validate_css(self, css: str) -> Dict[str, Any]:
        """Valide la qualité générale du CSS."""
        issues = []
        score = 100

        # Vérifier règles critiques
        for rule_name, pattern in self.critical_rules.items():
            if not re.search(pattern, css, re.IGNORECASE | re.DOTALL):
                issues.append(
                    {
                        "type": f"missing_{rule_name}",
                        "severity": "critical",
                        "message": f"Missing critical rule: {rule_name}",
                    }
                )
                score -= 15

        # Vérifier longueur CSS (pas trop court)
        if len(css) < 500:
            issues.append(
                {
                    "type": "insufficient_css",
                    "severity": "warning",
                    "message": "CSS appears to be too minimal",
                }
            )
            score -= 10

        return {
            "valid": len([i for i in issues if i["severity"] == "critical"])
            == 0,
            "score": max(0, score),
            "issues": issues,
        }

    def validate_pagination_quality(self, css: str) -> Dict[str, bool]:
        """Valide spécifiquement les règles de pagination."""
        return {
            "orphans_protection": bool(re.search(r"orphans:\s*[4-9]", css)),
            "widows_protection": bool(re.search(r"widows:\s*[4-9]", css)),
            "title_protection": bool(
                re.search(r"page-break-after:\s*avoid", css)
            ),
            "page_size_defined": bool(re.search(r"size:\s*[\d\w\s]+", css)),
        }

    def validate_typography_quality(
        self, css: str
    ) -> Dict[str, Union[bool, float]]:
        """Valide la qualité typographique."""
        font_quality = 0.5  # Base score

        # Vérifier police de qualité (serif)
        if re.search(
            r"serif|Times|Georgia|Crimson\s*Text", css, re.IGNORECASE
        ):
            font_quality += 0.3

        # Vérifier police de qualité (sans-serif)
        if re.search(
            r"sans-serif|Arial|Source\s*Sans|Helvetica", css, re.IGNORECASE
        ):
            font_quality += 0.3

        # Bonus pour Google Fonts
        if "googleapis.com" in css:
            font_quality += 0.2

        return {
            "font_quality": min(1.0, font_quality),
            "hyphenation_setup": bool(re.search(r"hyphens:\s*auto", css)),
            "line_height_optimal": bool(
                re.search(r"line-height:\s*[1-2]\.[0-9]", css)
            ),
        }

    def generate_quality_report(self, css: str) -> Dict[str, Any]:
        """Génère un rapport complet de qualité."""
        pagination = self.validate_pagination_quality(css)
        typography = self.validate_typography_quality(css)
        general = self.validate_css(css)

        # Score global
        category_scores = {
            "pagination": sum(pagination.values()) / len(pagination) * 100,
            "typography": (
                typography["font_quality"] * 0.4
                + (1 if typography["hyphenation_setup"] else 0) * 0.3
                + (1 if typography["line_height_optimal"] else 0) * 0.3
            )
            * 100,
            "layout": general["score"],
        }

        overall_score = sum(category_scores.values()) / len(category_scores)

        # Recommandations
        recommendations = []
        if not pagination["orphans_protection"]:
            recommendations.append("Add orphans protection (orphans: 4)")
        if not typography["hyphenation_setup"]:
            recommendations.append("Enable French hyphenation (hyphens: auto)")

        return {
            "overall_score": round(overall_score, 1),
            "categories": category_scores,
            "recommendations": recommendations,
            "critical_issues": [
                i for i in general["issues"] if i["severity"] == "critical"
            ],
        }

    def validate_performance(self, css: str) -> Dict[str, Union[bool, float]]:
        """Valide les performances du CSS."""
        css_size = len(css)

        # Calculer complexité basique
        selector_count = len(re.findall(r"[^}]+{", css))
        property_count = len(re.findall(r"[^:]+:[^;]+;", css))

        complexity_score = min(
            1.0, (selector_count + property_count / 2) / 1000
        )

        return {
            "size_warning": css_size > 50000,  # Plus de 50KB
            "complexity_score": complexity_score,
            "selector_count": selector_count,
            "estimated_render_time": complexity_score * 100,  # ms estimation
        }

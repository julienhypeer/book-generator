import React from 'react';
import { QualityValidationDetails } from './QualityValidationDetails';

export interface ExportOptionsData {
  format: 'pdf' | 'epub' | 'docx';
  template: 'roman' | 'technical' | 'academic';
  include_toc: boolean;
  quality_validation: boolean;
  body_font?: string;
  title_font?: string;
  font_size?: number;
  line_height?: number;
  toc_position?: 'beginning' | 'after_preface' | 'custom';
  toc_style?: 'simple' | 'dots' | 'aligned';
  toc_depth?: 1 | 2 | 3;
  toc_custom_position?: number;
}

interface ExportOptionsProps {
  options: ExportOptionsData;
  onChange: (options: ExportOptionsData) => void;
}

const formatDescriptions = {
  pdf: 'Livre professionnel pour impression avec pagination avancée',
  epub: 'Livre électronique pour liseuses (Kindle, Kobo, etc.)',
  docx: 'Document Word éditable pour révisions et collaboration',
};

// Ordre important : technical en premier par défaut
const templateDescriptions = {
  technical: 'Documentation technique - Mise en page structurée',
  roman: 'Roman, fiction, littéraire - Typographie classique',
  academic: 'Mémoire, thèse - Format universitaire avec notes',
};

const templateLabels = {
  technical: 'Technique',
  roman: 'Roman',
  academic: 'Académique',
};

// Polices disponibles pour le corps de texte
const bodyFonts = [
  { value: 'Times New Roman', label: 'Times New Roman (Classique)' },
  { value: 'Garamond', label: 'Garamond (Élégant)' },
  { value: 'Minion Pro', label: 'Minion Pro (Professionnel)' },
  { value: 'Sabon', label: 'Sabon (Littéraire)' },
  { value: 'Caslon', label: 'Caslon (Traditionnel)' },
  { value: 'Crimson Text', label: 'Crimson Text (Moderne)' },
];

// Polices disponibles pour les titres
const titleFonts = [
  { value: 'Helvetica', label: 'Helvetica (Net)' },
  { value: 'Arial', label: 'Arial (Standard)' },
  { value: 'Frutiger', label: 'Frutiger (Moderne)' },
  { value: 'Optima', label: 'Optima (Élégant)' },
  { value: 'Gill Sans', label: 'Gill Sans (Classique)' },
  { value: 'Source Sans Pro', label: 'Source Sans Pro (Technique)' },
];

export const ExportOptions: React.FC<ExportOptionsProps> = ({
  options,
  onChange,
}) => {
  const handleFormatChange = (format: ExportOptionsData['format']) => {
    onChange({ ...options, format });
  };

  const handleTemplateChange = (template: ExportOptionsData['template']) => {
    onChange({ ...options, template });
  };

  const handleToggleChange = (key: keyof Pick<ExportOptionsData, 'include_toc' | 'quality_validation'>) => {
    onChange({ ...options, [key]: !options[key] });
  };

  return (
    <div className="space-y-6">
      {/* Format Selection */}
      <div>
        <h3 className="text-lg font-medium mb-4">Format d'export</h3>
        <div className="space-y-3">
          {Object.entries(formatDescriptions).map(([format, description]) => (
            <label key={format} className="flex items-start space-x-3 cursor-pointer">
              <input
                type="radio"
                name="format"
                value={format}
                checked={options.format === format}
                onChange={() => handleFormatChange(format as ExportOptionsData['format'])}
                className="mt-1 h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-900 uppercase">
                  {format}
                </div>
                <div className="text-sm text-gray-600">
                  {description}
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Template Selection (PDF only) */}
      {options.format === 'pdf' && (
        <div>
          <h3 className="text-lg font-medium mb-4">Style du document</h3>
          <select
            value={options.template}
            onChange={(e) => handleTemplateChange(e.target.value as ExportOptionsData['template'])}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {Object.entries(templateDescriptions).map(([template, description]) => (
              <option key={template} value={template}>
                {templateLabels[template as keyof typeof templateLabels]} - {description}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Personnalisation des polices (PDF uniquement) */}
      {options.format === 'pdf' && (
        <div>
          <h3 className="text-lg font-medium mb-4">Personnalisation des polices</h3>
          <div className="space-y-4">
            {/* Police du corps de texte */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Police du texte principal
              </label>
              <select
                value={options.body_font || 'Times New Roman'}
                onChange={(e) => onChange({ ...options, body_font: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                {bodyFonts.map(font => (
                  <option key={font.value} value={font.value}>
                    {font.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Police des titres */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Police des titres
              </label>
              <select
                value={options.title_font || 'Helvetica'}
                onChange={(e) => onChange({ ...options, title_font: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                {titleFonts.map(font => (
                  <option key={font.value} value={font.value}>
                    {font.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Taille de police */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Taille du texte
                </label>
                <select
                  value={options.font_size || 11}
                  onChange={(e) => onChange({ ...options, font_size: parseInt(e.target.value) })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="10">10 pt (Petit)</option>
                  <option value="11">11 pt (Standard)</option>
                  <option value="12">12 pt (Grand)</option>
                </select>
              </div>

              {/* Interligne */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Interligne
                </label>
                <select
                  value={options.line_height || 1.4}
                  onChange={(e) => onChange({ ...options, line_height: parseFloat(e.target.value) })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="1.2">120% (Compact)</option>
                  <option value="1.4">140% (Standard)</option>
                  <option value="1.6">160% (Aéré)</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Export Options */}
      <div>
        <h3 className="text-lg font-medium mb-4">Options d'export</h3>
        <div className="space-y-4">
          {/* Table des matières */}
          <div className="border border-gray-200 rounded-lg p-4">
            <label className="flex items-center space-x-2 cursor-pointer mb-3">
              <input
                type="checkbox"
                checked={options.include_toc}
                onChange={() => handleToggleChange('include_toc')}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-gray-900 font-medium">Table des matières</span>
            </label>
            
            {options.include_toc && (
              <div className="ml-6 space-y-3">
                {/* Position de la TOC */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Position
                  </label>
                  <select
                    value={options.toc_position || 'beginning'}
                    onChange={(e) => onChange({ ...options, toc_position: e.target.value as any })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    <option value="beginning">Au début du livre</option>
                    <option value="after_preface">Après la préface</option>
                    <option value="custom">Position personnalisée</option>
                  </select>
                </div>
                
                {/* Position personnalisée */}
                {options.toc_position === 'custom' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Après le chapitre numéro
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={options.toc_custom_position || 1}
                      onChange={(e) => onChange({ ...options, toc_custom_position: parseInt(e.target.value) })}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>
                )}
                
                {/* Style de la TOC */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Style
                  </label>
                  <select
                    value={options.toc_style || 'dots'}
                    onChange={(e) => onChange({ ...options, toc_style: e.target.value as any })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    <option value="simple">Simple (titre seul)</option>
                    <option value="dots">Avec points de suite</option>
                    <option value="aligned">Numéros alignés à droite</option>
                  </select>
                </div>
                
                {/* Profondeur de la TOC */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Profondeur (niveaux de titres)
                  </label>
                  <select
                    value={options.toc_depth || 2}
                    onChange={(e) => onChange({ ...options, toc_depth: parseInt(e.target.value) as any })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    <option value="1">Chapitres uniquement (H1)</option>
                    <option value="2">Chapitres et sections (H1, H2)</option>
                    <option value="3">Tous les niveaux (H1, H2, H3)</option>
                  </select>
                </div>
              </div>
            )}
          </div>
          
          {options.format === 'pdf' && (
            <div>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.quality_validation}
                  onChange={() => handleToggleChange('quality_validation')}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-900">Validation qualité</span>
              </label>
              <QualityValidationDetails enabled={options.quality_validation} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
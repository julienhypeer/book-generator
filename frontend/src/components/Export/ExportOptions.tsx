import React from 'react';

export interface ExportOptionsData {
  format: 'pdf' | 'epub' | 'docx';
  template: 'roman' | 'technical' | 'academic';
  include_toc: boolean;
  quality_validation: boolean;
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

const templateDescriptions = {
  roman: 'Roman, fiction, littéraire - Typographie classique',
  technical: 'Documentation technique - Mise en page structurée',
  academic: 'Mémoire, thèse - Format universitaire avec notes',
};

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
          <h3 className="text-lg font-medium mb-4">Template</h3>
          <select
            value={options.template}
            onChange={(e) => handleTemplateChange(e.target.value as ExportOptionsData['template'])}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {Object.entries(templateDescriptions).map(([template, description]) => (
              <option key={template} value={template}>
                {template.charAt(0).toUpperCase() + template.slice(1)} - {description}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Export Options */}
      <div>
        <h3 className="text-lg font-medium mb-4">Options</h3>
        <div className="space-y-3">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={options.include_toc}
              onChange={() => handleToggleChange('include_toc')}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-gray-900">Table des matières</span>
          </label>
          
          {options.format === 'pdf' && (
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.quality_validation}
                onChange={() => handleToggleChange('quality_validation')}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-gray-900">Validation qualité</span>
              <span className="text-sm text-gray-500">(6 problèmes critiques)</span>
            </label>
          )}
        </div>
      </div>
    </div>
  );
};
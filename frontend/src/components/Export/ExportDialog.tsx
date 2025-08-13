import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Project } from '../../types';
import { ExportOptions, ExportOptionsData } from './ExportOptions';
import { exportProjectToPDF, exportProjectToEPUB, exportProjectToDocx } from '../../services/api';

interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  project: Project;
}

export const ExportDialog: React.FC<ExportDialogProps> = ({
  isOpen,
  onClose,
  project,
}) => {
  const [options, setOptions] = useState<ExportOptionsData>({
    format: 'pdf',
    template: 'technical',
    include_toc: true,
    quality_validation: true,
  });
  const [customFilename, setCustomFilename] = useState(project.title);

  const exportMutation = useMutation({
    mutationFn: async () => {
      let blob: Blob;
      let filename: string;

      const baseFilename = customFilename.trim() || project.title;
      
      switch (options.format) {
        case 'pdf':
          blob = await exportProjectToPDF(project.id, options);
          filename = `${baseFilename}.pdf`;
          break;
        case 'epub':
          blob = await exportProjectToEPUB(project.id, options);
          filename = `${baseFilename}.epub`;
          break;
        case 'docx':
          blob = await exportProjectToDocx(project.id, options);
          filename = `${baseFilename}.docx`;
          break;
        default:
          throw new Error(`Format non supporté: ${options.format}`);
      }

      return { blob, filename };
    },
    onSuccess: ({ blob, filename }) => {
      // Télécharger le fichier
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success(`Export ${options.format.toUpperCase()} terminé !`);
      onClose();
    },
    onError: (error) => {
      console.error('Export failed:', error);
      toast.error(`Erreur lors de l'export: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
    },
  });

  const handleExport = () => {
    exportMutation.mutate();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Exporter le livre
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              disabled={exportMutation.isPending}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Export du projet: {project.title}
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>Auteur: {project.author}</p>
                    <p>Mis à jour: {new Date(project.updated_at).toLocaleDateString('fr-FR')}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Nom du fichier personnalisé */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom du fichier
              </label>
              <input
                type="text"
                value={customFilename}
                onChange={(e) => setCustomFilename(e.target.value)}
                placeholder="Nom du fichier (sans extension)"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Le fichier sera enregistré sous : {customFilename || project.title}.{options.format}
              </p>
            </div>
            
            <ExportOptions 
              options={options} 
              onChange={setOptions} 
            />
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              disabled={exportMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Annuler
            </button>
            <button
              onClick={handleExport}
              disabled={exportMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exportMutation.isPending ? 'Export en cours...' : 'Exporter'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
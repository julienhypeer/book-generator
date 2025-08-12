import React from 'react';
import { Project } from '../../types';
import { Toolbar } from './Toolbar';

interface MainLayoutProps {
  project: Project;
  children: React.ReactNode;
  onSave?: () => void;
  onPreview?: () => void;
  onExport?: () => void;
  onSettings?: () => void;
  isSaving?: boolean;
  hasUnsavedChanges?: boolean;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  project,
  children,
  onSave = () => {},
  onPreview = () => {},
  onExport = () => {},
  onSettings = () => {},
  isSaving = false,
  hasUnsavedChanges = false,
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 md:px-6 lg:px-8" role="banner">
        <div className="flex items-center justify-between">
          {/* Project Info */}
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {project.title}
              </h1>
              <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                <span>Par {project.author}</span>
                <span>•</span>
                <span>Modifié le {formatDate(project.updated_at)}</span>
              </div>
            </div>
          </div>

          {/* Toolbar */}
          <Toolbar
            onSave={onSave}
            onPreview={onPreview}
            onExport={onExport}
            onSettings={onSettings}
            isSaving={isSaving}
            hasUnsavedChanges={hasUnsavedChanges}
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {children}
      </main>

      {/* Status Bar */}
      <div className="bg-gray-100 border-t border-gray-200 px-4 py-2 text-xs text-gray-600 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <span>Format: {project.settings?.page_format || 'A5'}</span>
          <span>•</span>
          <span>Police: {project.settings?.font_family || 'serif'}</span>
          <span>•</span>
          <span>Taille: {project.settings?.font_size || 12}pt</span>
        </div>
        
        <div className="flex items-center space-x-2">
          {hasUnsavedChanges && (
            <span className="inline-flex items-center text-orange-600">
              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 8 8">
                <circle cx="4" cy="4" r="3" />
              </svg>
              Non sauvegardé
            </span>
          )}
          
          <div className="text-gray-400">
            Book Generator v1.0
          </div>
        </div>
      </div>
    </div>
  );
};
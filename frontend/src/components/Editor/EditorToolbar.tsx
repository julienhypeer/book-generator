import React, { useState } from 'react';
import { useEditorStore } from '@/stores/editorStore';
import { useAutoSave } from '@/hooks/useAutoSave';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { chapterService } from '@/services/chapterService';
import { projectService } from '@/services/projectService';
import { toast } from 'react-hot-toast';
import {
  DocumentArrowUpIcon,
  Bars3Icon,
  EyeIcon,
  EyeSlashIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

export const EditorToolbar: React.FC = () => {
  const queryClient = useQueryClient();
  const {
    sidebarOpen,
    previewOpen,
    toggleSidebar,
    togglePreview,
    currentProject,
    setCurrentProject,
  } = useEditorStore();

  const { saveNow, isSaving, hasUnsavedChanges } = useAutoSave();
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');

  // Update project title mutation
  const updateTitleMutation = useMutation({
    mutationFn: async (title: string) => {
      if (!currentProject) throw new Error('No project selected');
      return projectService.updateProject(currentProject.id, { title });
    },
    onSuccess: (updatedProject) => {
      setCurrentProject(updatedProject);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Titre du projet mis à jour');
      setIsEditingTitle(false);
    },
    onError: () => {
      toast.error('Échec de la mise à jour du titre');
    },
  });

  // Import markdown mutation
  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      if (!currentProject) throw new Error('No project selected');
      
      const text = await file.text();
      return chapterService.importChapter(currentProject.id, text);
    },
    onSuccess: (newChapter) => {
      // Add the new chapter to the store immediately
      useEditorStore.getState().addChapter(newChapter);
      // Set it as active
      useEditorStore.getState().setActiveChapter(newChapter.id);
      // Invalidate chapters query to refresh the list from API
      queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
      toast.success('Chapitre importé avec succès');
    },
    onError: () => {
      toast.error('Échec de l\'importation du chapitre');
    },
  });


  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.md,.markdown,.txt';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        importMutation.mutate(file);
      }
    };
    input.click();
  };

  if (!currentProject) return null;

  return (
    <div className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-2">
      {/* Left section */}
      <div className="flex items-center gap-2">
        {/* Toggle sidebar */}
        <button
          onClick={toggleSidebar}
          className="rounded p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          title={sidebarOpen ? 'Masquer la barre latérale' : 'Afficher la barre latérale'}
        >
          <Bars3Icon className="h-5 w-5" />
        </button>

        {/* Project title */}
        <div className="ml-2">
          {isEditingTitle ? (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (editedTitle.trim()) {
                  updateTitleMutation.mutate(editedTitle.trim());
                }
              }}
              className="flex items-center"
            >
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                onBlur={() => {
                  if (editedTitle.trim() && editedTitle !== currentProject.title) {
                    updateTitleMutation.mutate(editedTitle.trim());
                  } else {
                    setIsEditingTitle(false);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Escape') {
                    setEditedTitle(currentProject.title);
                    setIsEditingTitle(false);
                  }
                }}
                className="text-lg font-semibold text-gray-900 bg-transparent border-b-2 border-blue-500 focus:outline-none"
                autoFocus
              />
            </form>
          ) : (
            <h1
              className="text-lg font-semibold text-gray-900 cursor-pointer hover:text-blue-600"
              onClick={() => {
                setEditedTitle(currentProject.title);
                setIsEditingTitle(true);
              }}
              title="Cliquez pour modifier le titre"
            >
              {currentProject.title}
            </h1>
          )}
        </div>

        {/* Save indicator */}
        {hasUnsavedChanges && (
          <div className="ml-4 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-orange-400" />
            <span className="text-sm text-gray-600">Modifications non enregistrées</span>
          </div>
        )}
      </div>

      {/* Center section */}
      <div className="flex items-center gap-2">
        {/* Import */}
        <button
          onClick={handleImport}
          disabled={importMutation.isPending}
          className="flex items-center gap-1 rounded px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100"
          title="Importer un fichier Markdown"
        >
          <DocumentArrowUpIcon className="h-4 w-4" />
          <span>Importer</span>
        </button>


        {/* Save now */}
        <button
          onClick={saveNow}
          disabled={!hasUnsavedChanges || isSaving}
          className="flex items-center gap-1 rounded bg-blue-500 px-3 py-1.5 text-sm text-white hover:bg-blue-600 disabled:opacity-50"
          title="Enregistrer maintenant (Ctrl+S)"
        >
          {isSaving ? (
            <>
              <ArrowPathIcon className="h-4 w-4 animate-spin" />
              <span>Enregistrement...</span>
            </>
          ) : (
            <>
              <span>Enregistrer</span>
            </>
          )}
        </button>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-2">
        {/* Toggle preview */}
        <button
          onClick={togglePreview}
          className="flex items-center gap-1 rounded p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          title={previewOpen ? 'Masquer la prévisualisation' : 'Afficher la prévisualisation'}
        >
          {previewOpen ? (
            <EyeSlashIcon className="h-5 w-5" />
          ) : (
            <EyeIcon className="h-5 w-5" />
          )}
        </button>

      </div>
    </div>
  );
};
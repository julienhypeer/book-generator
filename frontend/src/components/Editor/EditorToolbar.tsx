import React from 'react';
import { useEditorStore } from '@/stores/editorStore';
import { useAutoSave } from '@/hooks/useAutoSave';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { chapterService } from '@/services/chapterService';
import { toast } from 'react-hot-toast';
import {
  DocumentArrowDownIcon,
  DocumentArrowUpIcon,
  Bars3Icon,
  EyeIcon,
  EyeSlashIcon,
  Cog6ToothIcon,
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
    activeChapterId,
    chapters,
  } = useEditorStore();

  const { saveNow, isSaving, hasUnsavedChanges } = useAutoSave();

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
      toast.success('Chapter imported successfully');
    },
    onError: () => {
      toast.error('Failed to import chapter');
    },
  });

  // Export chapter mutation
  const exportChapterMutation = useMutation({
    mutationFn: async () => {
      if (!currentProject || !activeChapterId) {
        throw new Error('No chapter selected');
      }
      
      const markdown = await chapterService.exportChapter(
        currentProject.id,
        activeChapterId,
        true // Include metadata
      );
      
      // Download the markdown file
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      const chapter = chapters.find(c => c.id === activeChapterId);
      a.href = url;
      a.download = `${chapter?.title || 'chapter'}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    onSuccess: () => {
      toast.success('Chapter exported successfully');
    },
    onError: () => {
      toast.error('Failed to export chapter');
    },
  });

  // Export all chapters mutation
  const exportAllMutation = useMutation({
    mutationFn: async () => {
      if (!currentProject) throw new Error('No project selected');
      
      const markdown = await chapterService.exportAllChapters(
        currentProject.id,
        true // Include metadata
      );
      
      // Download the markdown file
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentProject.title || 'book'}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    onSuccess: () => {
      toast.success('All chapters exported successfully');
    },
    onError: () => {
      toast.error('Failed to export chapters');
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
          title={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
        >
          <Bars3Icon className="h-5 w-5" />
        </button>

        {/* Project title */}
        <div className="ml-2">
          <h1 className="text-lg font-semibold text-gray-900">
            {currentProject.title}
          </h1>
        </div>

        {/* Save indicator */}
        {hasUnsavedChanges && (
          <div className="ml-4 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-orange-400" />
            <span className="text-sm text-gray-600">Unsaved changes</span>
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
          title="Import markdown"
        >
          <DocumentArrowUpIcon className="h-4 w-4" />
          <span>Import</span>
        </button>

        {/* Export current chapter */}
        <button
          onClick={() => exportChapterMutation.mutate()}
          disabled={!activeChapterId || exportChapterMutation.isPending}
          className="flex items-center gap-1 rounded px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
          title="Export current chapter"
        >
          <DocumentArrowDownIcon className="h-4 w-4" />
          <span>Export Chapter</span>
        </button>

        {/* Export all */}
        <button
          onClick={() => exportAllMutation.mutate()}
          disabled={chapters.length === 0 || exportAllMutation.isPending}
          className="flex items-center gap-1 rounded px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
          title="Export all chapters"
        >
          <DocumentArrowDownIcon className="h-4 w-4" />
          <span>Export All</span>
        </button>

        {/* Save now */}
        <button
          onClick={saveNow}
          disabled={!hasUnsavedChanges || isSaving}
          className="flex items-center gap-1 rounded bg-blue-500 px-3 py-1.5 text-sm text-white hover:bg-blue-600 disabled:opacity-50"
          title="Save now (Ctrl+S)"
        >
          {isSaving ? (
            <>
              <ArrowPathIcon className="h-4 w-4 animate-spin" />
              <span>Saving...</span>
            </>
          ) : (
            <>
              <span>Save</span>
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
          title={previewOpen ? 'Hide preview' : 'Show preview'}
        >
          {previewOpen ? (
            <EyeSlashIcon className="h-5 w-5" />
          ) : (
            <EyeIcon className="h-5 w-5" />
          )}
        </button>

        {/* Settings */}
        <button
          className="rounded p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          title="Editor settings"
        >
          <Cog6ToothIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};
import React, { useState } from 'react';
import { useEditorStore } from '@/stores/editorStore';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { chapterService } from '@/services/chapterService';
import { toast } from 'react-hot-toast';
import { 
  PlusIcon, 
  TrashIcon, 
  DocumentTextIcon,
  ArrowUpTrayIcon,
  PencilIcon,
  DocumentIcon
} from '@heroicons/react/24/outline';

export const ChapterSidebar: React.FC = () => {
  const queryClient = useQueryClient();
  const {
    chapters,
    activeChapterId,
    setActiveChapter,
    currentProject,
    unsavedChanges,
  } = useEditorStore();

  const [newChapterTitle, setNewChapterTitle] = useState('');
  const [draggedChapterId, setDraggedChapterId] = useState<number | null>(null);
  const [dragOverChapterId, setDragOverChapterId] = useState<number | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingChapterId, setEditingChapterId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [isCreatingBlankPage, setIsCreatingBlankPage] = useState(false);

  // Create chapter mutation
  const createMutation = useMutation({
    mutationFn: async ({ title, isBlankPage = false }: { title: string; isBlankPage?: boolean }) => {
      if (!currentProject) throw new Error('No project selected');
      const content = isBlankPage ? '<!-- PAGE_BLANCHE_EDITORIALE -->' : '';
      return chapterService.createChapter(currentProject.id, { title, content });
    },
    onSuccess: (newChapter) => {
      // Add the new chapter to the store immediately
      useEditorStore.getState().addChapter(newChapter);
      // Invalidate chapters query to refresh the list from API
      queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
      setActiveChapter(newChapter.id);
      setNewChapterTitle('');
      setIsCreating(false);
      toast.success('Chapitre créé avec succès');
    },
    onError: () => {
      toast.error('Échec de la création du chapitre');
    },
  });

  // Delete chapter mutation
  const deleteMutation = useMutation({
    mutationFn: async (chapterId: number) => {
      if (!currentProject) throw new Error('No project selected');
      return chapterService.deleteChapter(currentProject.id, chapterId);
    },
    onSuccess: (_, chapterId) => {
      // Remove the chapter from the store immediately
      useEditorStore.getState().deleteChapter(chapterId);
      // Invalidate chapters query to refresh the list from API
      queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
      toast.success('Chapitre supprimé avec succès');
    },
    onError: () => {
      toast.error('Échec de la suppression du chapitre');
    },
  });

  // Reorder chapters mutation
  const reorderMutation = useMutation({
    mutationFn: async (chapterIds: number[]) => {
      if (!currentProject) throw new Error('No project selected');
      
      // Convert chapter IDs to the format expected by the backend
      const reorderData = chapterIds.map((id, index) => ({
        chapter_id: id,
        new_position: index + 1
      }));
      
      // Call backend API to reorder chapters
      return chapterService.reorderChapters(currentProject.id, reorderData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
      toast.success('Chapitres réorganisés');
    },
    onError: () => {
      toast.error('Échec de la réorganisation des chapitres');
    },
  });

  const handleCreateChapter = (e: React.FormEvent) => {
    e.preventDefault();
    if (newChapterTitle.trim()) {
      createMutation.mutate({ title: newChapterTitle.trim(), isBlankPage: false });
    }
  };

  const handleCreateBlankPage = () => {
    const pageNumber = chapters.length + 1;
    createMutation.mutate({ 
      title: `Page blanche ${pageNumber}`, 
      isBlankPage: true 
    });
  };

  const handleDeleteChapter = (chapterId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce chapitre ?')) {
      deleteMutation.mutate(chapterId);
    }
  };

  // Rename chapter mutation
  const renameMutation = useMutation({
    mutationFn: async ({ chapterId, title }: { chapterId: number; title: string }) => {
      if (!currentProject) throw new Error('No project selected');
      return chapterService.updateChapter(currentProject.id, chapterId, { title });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
      toast.success('Chapitre renommé');
      setEditingChapterId(null);
      setEditingTitle('');
    },
    onError: () => {
      toast.error('Échec du renommage du chapitre');
    },
  });

  const handleStartRename = (chapter: any) => {
    setEditingChapterId(chapter.id);
    setEditingTitle(chapter.title);
  };

  const handleRename = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingChapterId && editingTitle.trim()) {
      renameMutation.mutate({ chapterId: editingChapterId, title: editingTitle.trim() });
    }
  };

  const handleCancelRename = () => {
    setEditingChapterId(null);
    setEditingTitle('');
  };

  // Import multiple files
  const handleImportFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!currentProject || !e.target.files) return;
    
    const files = Array.from(e.target.files);
    
    for (const file of files) {
      if (file.type === 'text/markdown' || file.name.endsWith('.md')) {
        const content = await file.text();
        const title = file.name.replace('.md', '');
        await chapterService.createChapter(currentProject.id, { title, content });
      }
    }
    
    queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
    toast.success(`${files.length} chapitre(s) importé(s)`);
    e.target.value = ''; // Reset input
  };

  const sortedChapters = [...chapters].sort((a, b) => a.position - b.position);

  return (
    <div className="flex h-full flex-col">
      {/* Drag & Drop Indicator */}
      <div className="bg-green-100 text-green-800 px-4 py-2 text-xs font-bold text-center border-b border-green-200">
        🎯 DRAG & DROP ACTIVÉ 🎯
      </div>
      
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">Chapitres</h2>
          <div className="flex items-center gap-1">
            <label
              htmlFor="import-files"
              className="cursor-pointer rounded p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
              title="Importer des fichiers Markdown"
            >
              <ArrowUpTrayIcon className="h-5 w-5" />
              <input
                id="import-files"
                type="file"
                multiple
                accept=".md,text/markdown"
                onChange={handleImportFiles}
                className="hidden"
              />
            </label>
            <button
              onClick={handleCreateBlankPage}
              className="rounded p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
              title="Ajouter une page blanche"
            >
              <DocumentIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setIsCreating(true)}
              className="rounded p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
              title="Ajouter un nouveau chapitre"
            >
              <PlusIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* New chapter form */}
      {isCreating && (
        <form onSubmit={handleCreateChapter} className="border-b border-gray-200 p-3">
          <input
            type="text"
            value={newChapterTitle}
            onChange={(e) => setNewChapterTitle(e.target.value)}
            placeholder="Titre du chapitre..."
            className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
            autoFocus
            onBlur={() => {
              if (!newChapterTitle.trim()) {
                setIsCreating(false);
              }
            }}
          />
          <div className="mt-2 flex gap-2">
            <button
              type="submit"
              disabled={!newChapterTitle.trim() || createMutation.isPending}
              className="flex-1 rounded bg-blue-500 px-2 py-1 text-xs text-white hover:bg-blue-600 disabled:opacity-50"
            >
              Créer
            </button>
            <button
              type="button"
              onClick={() => {
                setIsCreating(false);
                setNewChapterTitle('');
              }}
              className="flex-1 rounded border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      {/* Chapter list */}
      <div className="flex-1 overflow-y-auto">
        {sortedChapters.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500">
            Aucun chapitre pour le moment
          </div>
        ) : (
          <ul className="py-1">
            {sortedChapters.map((chapter) => {
              const hasUnsaved = unsavedChanges.has(chapter.id);
              const isActive = chapter.id === activeChapterId;

              return (
                <li
                  key={chapter.id}
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.effectAllowed = 'move';
                    setDraggedChapterId(chapter.id);
                  }}
                  onDragOver={(e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    setDragOverChapterId(chapter.id);
                  }}
                  onDragLeave={() => {
                    setDragOverChapterId(null);
                  }}
                  onDrop={(e) => {
                    e.preventDefault();
                    if (draggedChapterId && draggedChapterId !== chapter.id) {
                      const draggedChapter = chapters.find(c => c.id === draggedChapterId);
                      const targetChapter = chapter;
                      if (draggedChapter && targetChapter) {
                        const newChapters = [...chapters];
                        const draggedIndex = newChapters.findIndex(c => c.id === draggedChapterId);
                        const targetIndex = newChapters.findIndex(c => c.id === chapter.id);
                        const [removed] = newChapters.splice(draggedIndex, 1);
                        newChapters.splice(targetIndex, 0, removed);
                        const chapterIds = newChapters.map(c => c.id);
                        reorderMutation.mutate(chapterIds);
                      }
                    }
                    setDraggedChapterId(null);
                    setDragOverChapterId(null);
                  }}
                  className={`group relative transition-all ${
                    isActive ? 'bg-blue-50' : 'hover:bg-gray-50'
                  } ${
                    dragOverChapterId === chapter.id ? 'border-t-2 border-blue-500' : ''
                  } ${
                    draggedChapterId === chapter.id ? 'opacity-50' : ''
                  }`}
                >
                  <div className="flex items-center min-w-0">
                    {editingChapterId === chapter.id ? (
                      <form onSubmit={handleRename} className="flex flex-1 items-center px-4 py-1">
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          className="flex-1 rounded border border-blue-400 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
                          autoFocus
                          onBlur={handleCancelRename}
                        />
                      </form>
                    ) : (
                      <button
                        onClick={() => setActiveChapter(chapter.id)}
                        className={`flex flex-1 items-center gap-2 px-4 py-2 text-left text-sm min-w-0 ${
                          isActive ? 'text-blue-700' : 'text-gray-700'
                        }`}
                      >
                        {chapter.content?.includes('PAGE_BLANCHE_EDITORIALE') ? (
                          <DocumentIcon className="h-4 w-4 flex-shrink-0" />
                        ) : (
                          <DocumentTextIcon className="h-4 w-4 flex-shrink-0" />
                        )}
                        <span className="truncate" style={{ maxWidth: '150px' }}>{chapter.title}</span>
                        {hasUnsaved && (
                          <span className="h-2 w-2 flex-shrink-0 rounded-full bg-orange-400 ml-1" />
                        )}
                      </button>
                    )}

                    {/* Actions */}
                    <div className="flex items-center gap-1 px-2 flex-shrink-0 opacity-0 group-hover:opacity-100">
                      {/* Rename */}
                      <button
                        onClick={() => handleStartRename(chapter)}
                        className="rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600"
                        title="Renommer le chapitre"
                      >
                        <PencilIcon className="h-3 w-3" />
                      </button>

                      {/* Drag handle - 6 dots icon */}
                      <div
                        className="cursor-move rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600"
                        title="Glisser pour réorganiser"
                        onMouseDown={() => setDraggedChapterId(chapter.id)}
                      >
                        <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 24 24">
                          <circle cx="9" cy="5" r="1" />
                          <circle cx="9" cy="12" r="1" />
                          <circle cx="9" cy="19" r="1" />
                          <circle cx="15" cy="5" r="1" />
                          <circle cx="15" cy="12" r="1" />
                          <circle cx="15" cy="19" r="1" />
                        </svg>
                      </div>

                      {/* Delete */}
                      <button
                        onClick={() => handleDeleteChapter(chapter.id)}
                        className="rounded p-1 text-gray-400 hover:bg-red-100 hover:text-red-600"
                        title="Supprimer le chapitre"
                      >
                        <TrashIcon className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Footer with chapter count */}
      <div className="border-t border-gray-200 px-4 py-2">
        <p className="text-xs text-gray-500">
          {chapters.length} chapitre{chapters.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  );
};
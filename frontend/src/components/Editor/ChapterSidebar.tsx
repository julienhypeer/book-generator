import React, { useState } from 'react';
import { useEditorStore } from '@/stores/editorStore';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { chapterService } from '@/services/chapterService';
import { toast } from 'react-hot-toast';
import { 
  PlusIcon, 
  TrashIcon, 
  DocumentTextIcon,
  ChevronUpIcon,
  ChevronDownIcon 
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
  const [isCreating, setIsCreating] = useState(false);

  // Create chapter mutation
  const createMutation = useMutation({
    mutationFn: async (title: string) => {
      if (!currentProject) throw new Error('No project selected');
      return chapterService.createChapter(currentProject.id, { title });
    },
    onSuccess: (newChapter) => {
      // Add the new chapter to the store immediately
      useEditorStore.getState().addChapter(newChapter);
      // Invalidate chapters query to refresh the list from API
      queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
      setActiveChapter(newChapter.id);
      setNewChapterTitle('');
      setIsCreating(false);
      toast.success('Chapter created successfully');
    },
    onError: () => {
      toast.error('Failed to create chapter');
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
      toast.success('Chapter deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete chapter');
    },
  });

  // Reorder chapters mutation
  const reorderMutation = useMutation({
    mutationFn: async ({ chapterId, direction }: { chapterId: number; direction: 'up' | 'down' }) => {
      if (!currentProject) throw new Error('No project selected');
      
      const chapter = chapters.find(c => c.id === chapterId);
      if (!chapter) throw new Error('Chapter not found');
      
      const newPosition = direction === 'up' ? chapter.position - 1 : chapter.position + 1;
      
      if (newPosition < 1 || newPosition > chapters.length) {
        throw new Error('Invalid position');
      }

      return chapterService.updateChapter(currentProject.id, chapterId, {
        position: newPosition,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chapters', currentProject?.id] });
      toast.success('Chapter reordered');
    },
    onError: () => {
      toast.error('Failed to reorder chapter');
    },
  });

  const handleCreateChapter = (e: React.FormEvent) => {
    e.preventDefault();
    if (newChapterTitle.trim()) {
      createMutation.mutate(newChapterTitle.trim());
    }
  };

  const handleDeleteChapter = (chapterId: number) => {
    if (window.confirm('Are you sure you want to delete this chapter?')) {
      deleteMutation.mutate(chapterId);
    }
  };

  const sortedChapters = [...chapters].sort((a, b) => a.position - b.position);

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">Chapters</h2>
          <button
            onClick={() => setIsCreating(true)}
            className="rounded p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            title="Add new chapter"
          >
            <PlusIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* New chapter form */}
      {isCreating && (
        <form onSubmit={handleCreateChapter} className="border-b border-gray-200 p-3">
          <input
            type="text"
            value={newChapterTitle}
            onChange={(e) => setNewChapterTitle(e.target.value)}
            placeholder="Chapter title..."
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
              Create
            </button>
            <button
              type="button"
              onClick={() => {
                setIsCreating(false);
                setNewChapterTitle('');
              }}
              className="flex-1 rounded border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Chapter list */}
      <div className="flex-1 overflow-y-auto">
        {sortedChapters.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500">
            No chapters yet
          </div>
        ) : (
          <ul className="py-1">
            {sortedChapters.map((chapter) => {
              const hasUnsaved = unsavedChanges.has(chapter.id);
              const isActive = chapter.id === activeChapterId;

              return (
                <li
                  key={chapter.id}
                  className={`group relative ${
                    isActive ? 'bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center">
                    <button
                      onClick={() => setActiveChapter(chapter.id)}
                      className={`flex flex-1 items-center gap-2 px-4 py-2 text-left text-sm ${
                        isActive ? 'text-blue-700' : 'text-gray-700'
                      }`}
                    >
                      <DocumentTextIcon className="h-4 w-4 flex-shrink-0" />
                      <span className="flex-1 truncate">{chapter.title}</span>
                      {hasUnsaved && (
                        <span className="h-2 w-2 flex-shrink-0 rounded-full bg-orange-400" />
                      )}
                    </button>

                    {/* Actions */}
                    <div className="flex items-center gap-1 px-2 opacity-0 group-hover:opacity-100">
                      {/* Move up */}
                      <button
                        onClick={() => reorderMutation.mutate({ chapterId: chapter.id, direction: 'up' })}
                        disabled={chapter.position === 1}
                        className="rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600 disabled:opacity-30"
                        title="Move up"
                      >
                        <ChevronUpIcon className="h-3 w-3" />
                      </button>

                      {/* Move down */}
                      <button
                        onClick={() => reorderMutation.mutate({ chapterId: chapter.id, direction: 'down' })}
                        disabled={chapter.position === chapters.length}
                        className="rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600 disabled:opacity-30"
                        title="Move down"
                      >
                        <ChevronDownIcon className="h-3 w-3" />
                      </button>

                      {/* Delete */}
                      <button
                        onClick={() => handleDeleteChapter(chapter.id)}
                        className="rounded p-1 text-gray-400 hover:bg-red-100 hover:text-red-600"
                        title="Delete chapter"
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
          {chapters.length} chapter{chapters.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  );
};
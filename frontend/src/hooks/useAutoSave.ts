import { useEffect, useRef, useCallback } from 'react';
import { useEditorStore } from '@/stores/editorStore';
import { useMutation } from '@tanstack/react-query';
import { chapterService } from '@/services/chapterService';
import { toast } from 'react-hot-toast';

export const useAutoSave = () => {
  const { 
    content, 
    unsavedChanges, 
    chapters,
    markChapterSaved,
    settings,
    currentProject 
  } = useEditorStore();
  
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const saveMutation = useMutation({
    mutationFn: async ({ chapterId, content }: { chapterId: number; content: string }) => {
      if (!currentProject) throw new Error('No project selected');
      
      const chapter = chapters.find(c => c.id === chapterId);
      if (!chapter) throw new Error('Chapter not found');
      
      return chapterService.updateChapter(
        currentProject.id,
        chapterId,
        { content }
      );
    },
    onSuccess: (_, variables) => {
      markChapterSaved(variables.chapterId);
    },
    onError: (error) => {
      console.error('Auto-save failed:', error);
      toast.error('Failed to auto-save. Please save manually.');
    },
  });

  useEffect(() => {
    if (!settings.autoSave || unsavedChanges.size === 0) {
      return;
    }

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout for auto-save
    timeoutRef.current = setTimeout(() => {
      // Save all unsaved chapters
      unsavedChanges.forEach((chapterId) => {
        const chapterContent = content.get(chapterId);
        if (chapterContent !== undefined) {
          saveMutation.mutate({ 
            chapterId, 
            content: chapterContent 
          });
        }
      });
    }, settings.autoSaveDelay);

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [
    content,
    unsavedChanges,
    settings.autoSave,
    settings.autoSaveDelay,
    saveMutation
  ]);

  // Manual save function
  const saveNow = useCallback(() => {
    unsavedChanges.forEach((chapterId) => {
      const chapterContent = content.get(chapterId);
      if (chapterContent !== undefined) {
        saveMutation.mutate({ 
          chapterId, 
          content: chapterContent 
        });
      }
    });
  }, [unsavedChanges, content, saveMutation]);

  return { 
    saveNow, 
    isSaving: saveMutation.isPending,
    hasUnsavedChanges: unsavedChanges.size > 0 
  };
};
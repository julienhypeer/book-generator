import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Chapter, Project, EditorSettings } from '@/types';

interface EditorState {
  // Project data
  currentProject: Project | null;
  project: Project | null;
  chapters: Chapter[];
  activeChapterId: number | null;
  
  // Editor content
  content: Map<number, string>;
  unsavedChanges: Set<number>;
  
  // Editor settings
  settings: EditorSettings;
  
  // UI state
  isLoading: boolean;
  isSaving: boolean;
  sidebarOpen: boolean;
  previewOpen: boolean;
  
  // Actions
  setProject: (project: Project) => void;
  loadProject: (project: Project) => void;
  saveProject: (project: Project) => Promise<void>;
  setChapters: (chapters: Chapter[]) => void;
  setActiveChapter: (chapterId: number) => void;
  addChapter: (chapter: Chapter) => void;
  updateChapter: (chapter: Chapter) => void;
  deleteChapter: (chapterId: number) => void;
  updateChapterContent: (chapterId: number, content: string) => void;
  markChapterSaved: (chapterId: number) => void;
  updateSettings: (settings: Partial<EditorSettings>) => void;
  toggleSidebar: () => void;
  togglePreview: () => void;
  reset: () => void;
  
  // Memory management
  clearUnusedContent: () => void;
  trimContentHistory: (maxSize?: number) => void;
  getMemoryUsage: () => { chapters: number; contentSize: number; totalSize: number };
  cleanup: () => void;
}

const defaultSettings: EditorSettings = {
  fontSize: 14,
  lineHeight: 1.6,
  wordWrap: 'on',
  minimap: false,
  theme: 'vs',
  autoSave: true,
  autoSaveDelay: 30000, // 30 seconds
};

export const useEditorStore = create<EditorState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        currentProject: null,
        
        // Getters
        get project() {
          return get().currentProject;
        },
        
        chapters: [],
        activeChapterId: null,
        content: new Map(),
        unsavedChanges: new Set(),
        settings: defaultSettings,
        isLoading: false,
        isSaving: false,
        sidebarOpen: true,
        previewOpen: false,
        
        // Actions
        setProject: (project) => 
          set({ currentProject: project }),
        
        loadProject: (project) =>
          set({ currentProject: project }),
        
        saveProject: async (project) => {
          set({ isSaving: true });
          try {
            // Mock save - in real app would call API
            await new Promise(resolve => setTimeout(resolve, 1000));
            set({ 
              currentProject: { ...project, updated_at: new Date().toISOString() },
              unsavedChanges: new Set()
            });
          } finally {
            set({ isSaving: false });
          }
        },
        
        setChapters: (chapters) => {
          const content = new Map();
          chapters.forEach(chapter => {
            content.set(chapter.id, chapter.content);
          });
          set({ 
            chapters, 
            content,
            activeChapterId: chapters.length > 0 ? chapters[0].id : null 
          });
        },
        
        setActiveChapter: (chapterId) => 
          set({ activeChapterId: chapterId }),
        
        addChapter: (chapter) => {
          const newChapters = [...get().chapters, chapter];
          const newContent = new Map(get().content);
          newContent.set(chapter.id, chapter.content);
          set({
            chapters: newChapters,
            content: newContent,
          });
        },
        
        updateChapter: (chapter) => {
          const newChapters = get().chapters.map(c => 
            c.id === chapter.id ? chapter : c
          );
          set({ chapters: newChapters });
        },
        
        deleteChapter: (chapterId) => {
          const newChapters = get().chapters.filter(c => c.id !== chapterId);
          const newContent = new Map(get().content);
          newContent.delete(chapterId);
          const newUnsaved = new Set(get().unsavedChanges);
          newUnsaved.delete(chapterId);
          
          set({
            chapters: newChapters,
            content: newContent,
            unsavedChanges: newUnsaved,
            activeChapterId: get().activeChapterId === chapterId ? null : get().activeChapterId,
          });
        },
        
        updateChapterContent: (chapterId, content) => {
          const newContent = new Map(get().content);
          newContent.set(chapterId, content);
          const newUnsaved = new Set(get().unsavedChanges);
          newUnsaved.add(chapterId);
          set({ 
            content: newContent, 
            unsavedChanges: newUnsaved 
          });
        },
        
        markChapterSaved: (chapterId) => {
          const newUnsaved = new Set(get().unsavedChanges);
          newUnsaved.delete(chapterId);
          set({ unsavedChanges: newUnsaved });
        },
        
        updateSettings: (settings) =>
          set((state) => ({
            settings: { ...state.settings, ...settings }
          })),
        
        toggleSidebar: () =>
          set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        
        togglePreview: () =>
          set((state) => ({ previewOpen: !state.previewOpen })),
        
        reset: () =>
          set({
            currentProject: null,
            chapters: [],
            activeChapterId: null,
            content: new Map(),
            unsavedChanges: new Set(),
            isLoading: false,
            isSaving: false,
          }),
        
        // Memory management methods
        clearUnusedContent: () => {
          const state = get();
          const activeChapterIds = new Set(state.chapters.map(c => c.id));
          const newContent = new Map();
          const newUnsaved = new Set();
          
          // Keep only content for existing chapters
          state.content.forEach((content, chapterId) => {
            if (activeChapterIds.has(chapterId)) {
              newContent.set(chapterId, content);
            }
          });
          
          // Clean up unsaved changes for removed chapters
          state.unsavedChanges.forEach(chapterId => {
            if (activeChapterIds.has(chapterId)) {
              newUnsaved.add(chapterId);
            }
          });
          
          set({ content: newContent, unsavedChanges: newUnsaved });
        },
        
        trimContentHistory: (maxSize = 50) => {
          const state = get();
          
          if (state.chapters.length > maxSize) {
            // Keep only recent chapters and their content
            const recentChapters = state.chapters.slice(-maxSize);
            const recentChapterIds = new Set(recentChapters.map(c => c.id));
            const newContent = new Map();
            const newUnsaved = new Set();
            
            recentChapters.forEach(chapter => {
              const content = state.content.get(chapter.id);
              if (content) {
                newContent.set(chapter.id, content);
              }
              if (state.unsavedChanges.has(chapter.id)) {
                newUnsaved.add(chapter.id);
              }
            });
            
            set({
              chapters: recentChapters,
              content: newContent,
              unsavedChanges: newUnsaved,
              activeChapterId: recentChapterIds.has(state.activeChapterId || 0) 
                ? state.activeChapterId 
                : recentChapters[0]?.id || null
            });
          }
        },
        
        getMemoryUsage: () => {
          const state = get();
          let contentSize = 0;
          
          state.content.forEach(content => {
            contentSize += content.length * 2; // Rough estimate: 2 bytes per character
          });
          
          const totalSize = contentSize + (state.chapters.length * 500); // Rough chapter metadata size
          
          return {
            chapters: state.chapters.length,
            contentSize: Math.round(contentSize / 1024), // KB
            totalSize: Math.round(totalSize / 1024) // KB
          };
        },
        
        cleanup: () => {
          const actions = get();
          
          // Clear unused content
          actions.clearUnusedContent();
          
          // Trim if too many chapters (performance threshold)
          if (actions.chapters.length > 100) {
            actions.trimContentHistory(100);
          }
          
          // Force garbage collection hint
          if (window.gc) {
            window.gc();
          }
        },
      }),
      {
        name: 'editor-store',
        partialize: (state) => ({
          settings: state.settings,
          sidebarOpen: state.sidebarOpen,
          previewOpen: state.previewOpen,
        }),
      }
    )
  )
);
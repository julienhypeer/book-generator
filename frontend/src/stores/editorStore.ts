import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Chapter, Project, EditorSettings } from '@/types';

interface EditorState {
  // Project data
  currentProject: Project | null;
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
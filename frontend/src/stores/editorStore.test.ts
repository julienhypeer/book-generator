import { describe, it, expect, beforeEach } from 'vitest';
import { useEditorStore } from './editorStore';

describe('editorStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useEditorStore.setState({
      currentProject: null,
      chapters: [],
      activeChapterId: null,
      content: new Map(),
      unsavedChanges: new Set(),
      sidebarOpen: true,
      previewOpen: false,
      settings: {
        autoSave: true,
        autoSaveDelay: 30000,
        fontSize: 14,
        lineHeight: 1.5,
        wordWrap: 'on',
        minimap: false,
        theme: 'vs-light',
      },
    });
  });

  describe('Project Management', () => {
    it('loads a project', () => {
      const project = {
        id: 1,
        title: 'Test Project',
        description: 'Test Description',
        author: 'Test Author',
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
        settings: {
          page_format: 'A5' as const,
          font_family: 'serif',
          font_size: 12,
          line_height: 1.5,
          margins: { top: 20, bottom: 20, left: 15, right: 15 },
          hyphenation: true,
          page_numbers: true,
          table_of_contents: true,
        },
      };

      useEditorStore.getState().loadProject(project);
      
      expect(useEditorStore.getState().currentProject).toEqual(project);
    });
  });

  describe('Chapter Management', () => {
    it('sets chapters', () => {
      const chapters = [
        {
          id: 1,
          project_id: 1,
          title: 'Chapter 1',
          content: 'Content 1',
          position: 1,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
        {
          id: 2,
          project_id: 1,
          title: 'Chapter 2',
          content: 'Content 2',
          position: 2,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ];

      useEditorStore.getState().setChapters(chapters);
      
      expect(useEditorStore.getState().chapters).toEqual(chapters);
      expect(useEditorStore.getState().content.get(1)).toBe('Content 1');
      expect(useEditorStore.getState().content.get(2)).toBe('Content 2');
    });

    it('sets active chapter', () => {
      useEditorStore.getState().setActiveChapter(5);
      expect(useEditorStore.getState().activeChapterId).toBe(5);
    });

    it('adds a chapter', () => {
      const chapter = {
        id: 3,
        project_id: 1,
        title: 'New Chapter',
        content: 'New Content',
        position: 1,
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
      };

      useEditorStore.getState().addChapter(chapter);
      
      expect(useEditorStore.getState().chapters).toContainEqual(chapter);
      expect(useEditorStore.getState().content.get(3)).toBe('New Content');
    });

    it('updates a chapter', () => {
      const initialChapter = {
        id: 1,
        project_id: 1,
        title: 'Initial Title',
        content: 'Initial Content',
        position: 1,
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
      };

      useEditorStore.getState().addChapter(initialChapter);
      
      const updatedChapter = { ...initialChapter, title: 'Updated Title' };
      useEditorStore.getState().updateChapter(updatedChapter);
      
      const chapter = useEditorStore.getState().chapters.find(c => c.id === 1);
      expect(chapter?.title).toBe('Updated Title');
    });

    it('deletes a chapter', () => {
      const chapter = {
        id: 1,
        project_id: 1,
        title: 'Chapter to Delete',
        content: 'Content',
        position: 1,
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
      };

      useEditorStore.getState().addChapter(chapter);
      useEditorStore.getState().deleteChapter(1);
      
      expect(useEditorStore.getState().chapters).toHaveLength(0);
      expect(useEditorStore.getState().content.has(1)).toBe(false);
      expect(useEditorStore.getState().unsavedChanges.has(1)).toBe(false);
    });
  });

  describe('Content Management', () => {
    it('updates chapter content', () => {
      useEditorStore.getState().updateChapterContent(1, 'New Content');
      
      expect(useEditorStore.getState().content.get(1)).toBe('New Content');
      expect(useEditorStore.getState().unsavedChanges.has(1)).toBe(true);
    });

    it('marks chapter as saved', () => {
      useEditorStore.getState().updateChapterContent(1, 'Content');
      useEditorStore.getState().markChapterSaved(1);
      
      expect(useEditorStore.getState().unsavedChanges.has(1)).toBe(false);
    });
  });

  describe('UI State', () => {
    it('toggles sidebar', () => {
      const initialState = useEditorStore.getState().sidebarOpen;
      useEditorStore.getState().toggleSidebar();
      
      expect(useEditorStore.getState().sidebarOpen).toBe(!initialState);
    });

    it('toggles preview', () => {
      const initialState = useEditorStore.getState().previewOpen;
      useEditorStore.getState().togglePreview();
      
      expect(useEditorStore.getState().previewOpen).toBe(!initialState);
    });

    it('updates settings', () => {
      useEditorStore.getState().updateSettings({ fontSize: 16, theme: 'vs-dark' });
      
      expect(useEditorStore.getState().settings.fontSize).toBe(16);
      expect(useEditorStore.getState().settings.theme).toBe('vs-dark');
    });
  });
});
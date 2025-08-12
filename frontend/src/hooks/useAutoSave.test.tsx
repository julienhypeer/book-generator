import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useAutoSave } from './useAutoSave';
import { useEditorStore } from '@/stores/editorStore';
import { chapterService } from '@/services/chapterService';

// Mock the chapter service
vi.mock('@/services/chapterService', () => ({
  chapterService: {
    updateChapter: vi.fn(),
  },
}));

// Mock toast
vi.mock('react-hot-toast', () => ({
  toast: {
    error: vi.fn(),
  },
}));

describe('useAutoSave', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    // Reset store
    useEditorStore.setState({
      currentProject: {
        id: 1,
        title: 'Test Project',
        description: 'Test',
        author: 'Test',
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
        settings: {
          page_format: 'A5',
          font_family: 'serif',
          font_size: 12,
          line_height: 1.5,
          margins: { top: 20, bottom: 20, left: 15, right: 15 },
          hyphenation: true,
          page_numbers: true,
          table_of_contents: true,
        },
      },
      chapters: [
        {
          id: 1,
          project_id: 1,
          title: 'Chapter 1',
          content: 'Content',
          position: 1,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ],
      content: new Map([[1, 'Updated Content']]),
      unsavedChanges: new Set([1]),
      settings: {
        autoSave: true,
        autoSaveDelay: 100, // Short delay for testing
        fontSize: 14,
        lineHeight: 1.5,
        wordWrap: 'on',
        minimap: false,
        theme: 'vs-light',
      },
    });

    // Clear all mocks
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('returns correct initial state', () => {
    const { result } = renderHook(() => useAutoSave(), { wrapper });
    
    expect(result.current.hasUnsavedChanges).toBe(true);
    expect(result.current.isSaving).toBe(false);
    expect(typeof result.current.saveNow).toBe('function');
  });

  it('auto-saves after delay when auto-save is enabled', () => {
    vi.mocked(chapterService.updateChapter).mockResolvedValue({
      id: 1,
      project_id: 1,
      title: 'Chapter 1',
      content: 'Updated Content',
      position: 1,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    });

    renderHook(() => useAutoSave(), { wrapper });

    // Fast-forward time to trigger auto-save
    act(() => {
      vi.advanceTimersByTime(100);
    });

    // The hook should have triggered the mutation
    // We'll check that the mutation was called, not wait for the promise
    expect(chapterService.updateChapter).toHaveBeenCalledWith(
      1,
      1,
      { content: 'Updated Content' }
    );
  });

  it('does not auto-save when auto-save is disabled', () => {
    useEditorStore.setState({
      settings: {
        ...useEditorStore.getState().settings,
        autoSave: false,
      },
    });

    renderHook(() => useAutoSave(), { wrapper });

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(chapterService.updateChapter).not.toHaveBeenCalled();
  });

  it('saves immediately when saveNow is called', async () => {
    vi.mocked(chapterService.updateChapter).mockResolvedValue({
      id: 1,
      project_id: 1,
      title: 'Chapter 1',
      content: 'Updated Content',
      position: 1,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    });

    const { result } = renderHook(() => useAutoSave(), { wrapper });

    await act(async () => {
      result.current.saveNow();
    });

    expect(chapterService.updateChapter).toHaveBeenCalledWith(
      1,
      1,
      { content: 'Updated Content' }
    );
  });

  it('does not save when there are no unsaved changes', () => {
    useEditorStore.setState({
      unsavedChanges: new Set(),
    });

    renderHook(() => useAutoSave(), { wrapper });

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(chapterService.updateChapter).not.toHaveBeenCalled();
  });

  it('calls saveNow immediately', () => {
    vi.mocked(chapterService.updateChapter).mockResolvedValue({
      id: 1,
      project_id: 1,
      title: 'Chapter 1',
      content: 'Updated Content',
      position: 1,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    });

    const { result } = renderHook(() => useAutoSave(), { wrapper });

    act(() => {
      result.current.saveNow();
    });

    // Just verify the function was called, don't wait for async operations
    expect(chapterService.updateChapter).toHaveBeenCalledWith(
      1,
      1,
      { content: 'Updated Content' }
    );
  });
});
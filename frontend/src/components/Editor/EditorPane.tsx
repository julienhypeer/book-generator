import React, { Suspense, lazy } from 'react';
import { useEditorStore } from '@/stores/editorStore';
import { ChapterSidebar } from './ChapterSidebar';
import { EditorToolbar } from './EditorToolbar';
import { EditorStatusBar } from './EditorStatusBar';
import { LoadingSpinner } from '@components/common/LoadingSpinner';
import { ResizablePanel } from '../Layout/ResizablePanel';

// Lazy load Monaco Editor for better performance
const MonacoEditor = lazy(() => 
  import('./MonacoEditor').then(module => ({ default: module.MonacoEditor }))
);

export const EditorPane: React.FC = () => {
  const {
    chapters,
    activeChapterId,
    content,
    sidebarOpen,
    previewOpen,
    currentProject,
  } = useEditorStore();

  const activeChapter = chapters.find((c) => c.id === activeChapterId);
  const chapterContent = activeChapterId ? content.get(activeChapterId) || '' : '';

  if (!currentProject) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-700">Aucun projet sélectionné</h2>
          <p className="mt-2 text-gray-500">Sélectionnez ou créez un projet pour commencer l'édition</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Toolbar */}
      <EditorToolbar />

      {/* Main editor area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        {sidebarOpen && (
          <ResizablePanel
            defaultWidth={256}
            minWidth={200}
            maxWidth={400}
            storageKey="chapter-sidebar-width"
            className="border-r border-gray-200 bg-white"
          >
            <ChapterSidebar />
          </ResizablePanel>
        )}

        {/* Editor */}
        <div className="flex flex-1 flex-col">
          {activeChapter ? (
            <>
              {/* Chapter title */}
              <div className="border-b border-gray-200 bg-white px-4 py-2">
                <h3 className="text-lg font-medium text-gray-900">
                  {activeChapter.title}
                </h3>
              </div>

              {/* Monaco Editor */}
              <div className="flex-1 overflow-hidden">
                <Suspense
                  fallback={
                    <div className="flex h-full items-center justify-center">
                      <LoadingSpinner />
                    </div>
                  }
                >
                  <MonacoEditor
                    key={activeChapterId}
                    chapterId={activeChapterId || 0}
                    content={chapterContent}
                  />
                </Suspense>
              </div>
            </>
          ) : (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <h3 className="text-xl font-medium text-gray-700">
                  Aucun chapitre sélectionné
                </h3>
                <p className="mt-2 text-gray-500">
                  Sélectionnez un chapitre dans la barre latérale ou créez-en un nouveau
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Preview pane (if open) */}
        {previewOpen && (
          <div className="w-1/2 border-l border-gray-200 bg-white">
            <div className="h-full p-4">
              <h3 className="mb-4 text-lg font-medium">Prévisualisation</h3>
              {/* Preview component will be added later */}
              <div className="rounded border border-gray-200 p-4">
                <p className="text-gray-500">La prévisualisation apparaîtra ici</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Status bar */}
      <EditorStatusBar />
    </div>
  );
};
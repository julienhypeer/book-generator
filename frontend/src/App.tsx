import { useEffect, useState, useCallback } from 'react';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
import { MainLayout } from './components/Layout';
import { EditorPane } from './components/Editor';
import { PreviewPane } from './components/Preview';
import { ExportDialog } from './components/Export';
import { useEditorStore } from './stores/editorStore';
import { useAutoSave } from './hooks/useAutoSave';
import { chapterService } from './services/chapterService';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes
      retry: 1,
    },
  },
});

function AppContent() {
  const { project, loadProject, saveProject, setChapters } = useEditorStore();
  const [showPreview, setShowPreview] = useState(false);
  const [showExport, setShowExport] = useState(false);
  // Settings not implemented yet
  // const [showSettings] = useState(false);

  // Auto-save functionality
  const { isSaving, hasUnsavedChanges } = useAutoSave();

  // Load chapters from API when project loads
  const { data: chapters, isLoading: chaptersLoading } = useQuery({
    queryKey: ['chapters', project?.id],
    queryFn: () => project ? chapterService.getChapters(project.id) : Promise.resolve([]),
    enabled: !!project,
    staleTime: 1000 * 60, // 1 minute
  });

  // Update store when chapters are loaded
  useEffect(() => {
    if (chapters) {
      setChapters(chapters);
    }
  }, [chapters, setChapters]);

  useEffect(() => {
    // Load the default project or last opened project
    // This is a mock - in real app, would fetch from API
    loadProject({
      id: 1,
      title: 'Mon Livre',
      description: 'Un projet de livre exemple',
      author: 'Auteur Exemple',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      settings: {
        page_format: 'A5',
        font_family: 'serif',
        font_size: 12,
        line_height: 1.5,
        margins: {
          top: 20,
          bottom: 20,
          left: 15,
          right: 15,
        },
        hyphenation: true,
        page_numbers: true,
        table_of_contents: true,
      },
    });
  }, [loadProject]);

  const handleSave = useCallback(async () => {
    if (!project) return;
    
    try {
      await saveProject(project);
      toast.success('Projet sauvegardé !');
    } catch (error) {
      console.error('Save failed:', error);
      toast.error('Erreur lors de la sauvegarde');
    }
  }, [project, saveProject]);

  const handlePreview = useCallback(() => {
    setShowPreview(!showPreview);
  }, [showPreview]);

  const handleExport = () => {
    setShowExport(true);
  };

  const handleSettings = () => {
    // setShowSettings(true);
    toast('Paramètres à venir...', { icon: '⚙️' });
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey) {
        switch (event.key) {
          case 's':
            event.preventDefault();
            handleSave();
            break;
          case 'p':
            event.preventDefault();
            handlePreview();
            break;
          case 'e':
            event.preventDefault();
            handleExport();
            break;
          case 'Escape':
            setShowPreview(false);
            setShowExport(false);
            // setShowSettings(false); // Not used currently
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlePreview, handleSave]);

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin mx-auto h-8 w-8 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>Chargement du projet...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <MainLayout
        project={project}
        onSave={handleSave}
        onPreview={handlePreview}
        onExport={handleExport}
        onSettings={handleSettings}
        isSaving={isSaving}
        hasUnsavedChanges={hasUnsavedChanges}
      >
        <EditorPane />
      </MainLayout>

      {/* Preview Pane */}
      <PreviewPane
        projectId={project.id}
        isVisible={showPreview}
        onClose={() => setShowPreview(false)}
        onExport={handleExport}
      />

      {/* Export Dialog */}
      {showExport && (
        <ExportDialog
          isOpen={showExport}
          onClose={() => setShowExport(false)}
          project={project}
        />
      )}

      {/* Toast Notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
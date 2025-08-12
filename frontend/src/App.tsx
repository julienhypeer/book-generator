import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import { EditorPane } from './components/Editor';
import { useEditorStore } from './stores/editorStore';

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
  const { loadProject } = useEditorStore();

  useEffect(() => {
    // Load the default project or last opened project
    // This is a mock - in real app, would fetch from API
    loadProject({
      id: 1,
      title: 'My Book Project',
      description: 'A sample book project',
      author: 'John Doe',
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

  return (
    <>
      <EditorPane />
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
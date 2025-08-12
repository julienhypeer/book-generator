import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './MainLayout';

const mockProject = {
  id: 1,
  title: 'Test Book',
  description: 'Test description',
  author: 'Test Author',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
  settings: {
    page_format: 'A5' as const,
    font_family: 'serif' as const,
    font_size: 12,
    line_height: 1.5,
    margins: { top: 20, bottom: 20, left: 15, right: 15 },
    hyphenation: true,
    page_numbers: true,
    table_of_contents: true,
  },
};

const renderWithQuery = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('MainLayout', () => {
  it('should render header with project title', () => {
    renderWithQuery(
      <MainLayout project={mockProject}>
        <div>Content</div>
      </MainLayout>
    );

    expect(screen.getByText('Test Book')).toBeInTheDocument();
  });

  it('should render main toolbar buttons', () => {
    renderWithQuery(
      <MainLayout project={mockProject}>
        <div>Content</div>
      </MainLayout>
    );

    expect(screen.getByRole('button', { name: /sauvegarder/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /prévisualiser/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /exporter/i })).toBeInTheDocument();
  });

  it('should render children content', () => {
    renderWithQuery(
      <MainLayout project={mockProject}>
        <div data-testid="child-content">Test Content</div>
      </MainLayout>
    );

    expect(screen.getByTestId('child-content')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should show keyboard shortcuts', () => {
    renderWithQuery(
      <MainLayout project={mockProject}>
        <div>Content</div>
      </MainLayout>
    );

    // Check for keyboard shortcut hints
    expect(screen.getByTitle(/Cmd\+S/i)).toBeInTheDocument();
    expect(screen.getByTitle(/Cmd\+P/i)).toBeInTheDocument();
    expect(screen.getByTitle(/Cmd\+E/i)).toBeInTheDocument();
  });

  it('should show author information', () => {
    renderWithQuery(
      <MainLayout project={mockProject}>
        <div>Content</div>
      </MainLayout>
    );

    expect(screen.getByText(/Par Test Author/)).toBeInTheDocument();
  });

  it('should show last updated time', () => {
    renderWithQuery(
      <MainLayout project={mockProject}>
        <div>Content</div>
      </MainLayout>
    );

    expect(screen.getByText(/Modifié le/i)).toBeInTheDocument();
  });

  it('should be responsive', () => {
    renderWithQuery(
      <MainLayout project={mockProject}>
        <div>Content</div>
      </MainLayout>
    );

    const header = screen.getByRole('banner');
    expect(header).toHaveClass('px-4', 'md:px-6', 'lg:px-8');
  });
});
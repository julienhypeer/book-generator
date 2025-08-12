import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ExportDialog } from './ExportDialog';

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn(),
  },
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn(),
  },
}));

// Mock API
vi.mock('../../services/api', () => ({
  exportProjectToPDF: vi.fn(),
  exportProjectToEPUB: vi.fn(),
  exportProjectToDocx: vi.fn(),
}));

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

describe('ExportDialog', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render dialog when open', () => {
    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    expect(screen.getByText('Exporter le livre')).toBeInTheDocument();
    expect(screen.getByText('Format d\'export')).toBeInTheDocument();
  });

  it('should not render dialog when closed', () => {
    renderWithQuery(
      <ExportDialog
        isOpen={false}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    expect(screen.queryByText('Exporter le livre')).not.toBeInTheDocument();
  });

  it('should show export format options', () => {
    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    expect(screen.getByRole('radio', { name: /PDF/i })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /EPUB/i })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /DOCX/i })).toBeInTheDocument();
  });

  it('should select PDF format by default', () => {
    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    const pdfRadio = screen.getByRole('radio', { name: /PDF/i });
    expect(pdfRadio).toBeChecked();
  });

  it('should show template options for PDF', () => {
    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    expect(screen.getByText('Template')).toBeInTheDocument();
    const templateSelect = screen.getByRole('combobox');
    expect(templateSelect).toBeInTheDocument();
    expect(templateSelect).toHaveValue('roman');
  });

  it('should hide template options for non-PDF formats', () => {
    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    const epubRadio = screen.getByRole('radio', { name: /EPUB/i });
    fireEvent.click(epubRadio);

    expect(screen.queryByText('Template')).not.toBeInTheDocument();
  });

  it('should call onClose when cancel button is clicked', () => {
    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /Annuler/i });
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should start export when export button is clicked', async () => {
    const { exportProjectToPDF } = await import('../../services/api');
    vi.mocked(exportProjectToPDF).mockResolvedValue(new Blob());

    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    const exportButton = screen.getByRole('button', { name: /Exporter/i });
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(exportProjectToPDF).toHaveBeenCalledWith(1, {
        format: 'pdf',
        template: 'roman',
        include_toc: true,
        quality_validation: true,
      });
    });
  });

  it('should disable export button during export', async () => {
    const { exportProjectToPDF } = await import('../../services/api');
    vi.mocked(exportProjectToPDF).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(new Blob()), 100))
    );

    renderWithQuery(
      <ExportDialog
        isOpen={true}
        onClose={mockOnClose}
        project={mockProject}
      />
    );

    const exportButton = screen.getByRole('button', { name: /Exporter/i });
    fireEvent.click(exportButton);

    // Wait for the mutation to start
    await waitFor(() => {
      expect(screen.getByText('Export en cours...')).toBeInTheDocument();
    }, { timeout: 1000 });

    // Button should be disabled during export
    const disabledButton = screen.getByRole('button', { name: /Export en cours/i });
    expect(disabledButton).toBeDisabled();
  });
});
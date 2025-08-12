import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Toolbar } from './Toolbar';

describe('Toolbar', () => {
  const mockOnSave = vi.fn();
  const mockOnPreview = vi.fn();
  const mockOnExport = vi.fn();
  const mockOnSettings = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render all toolbar buttons', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByRole('button', { name: /sauvegarder/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /prévisualiser/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /exporter/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /paramètres/i })).toBeInTheDocument();
  });

  it('should call onSave when save button is clicked', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    const saveButton = screen.getByRole('button', { name: /sauvegarder/i });
    fireEvent.click(saveButton);

    expect(mockOnSave).toHaveBeenCalledTimes(1);
  });

  it('should call onPreview when preview button is clicked', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    const previewButton = screen.getByRole('button', { name: /prévisualiser/i });
    fireEvent.click(previewButton);

    expect(mockOnPreview).toHaveBeenCalledTimes(1);
  });

  it('should call onExport when export button is clicked', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    const exportButton = screen.getByRole('button', { name: /exporter/i });
    fireEvent.click(exportButton);

    expect(mockOnExport).toHaveBeenCalledTimes(1);
  });

  it('should call onSettings when settings button is clicked', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    const settingsButton = screen.getByRole('button', { name: /paramètres/i });
    fireEvent.click(settingsButton);

    expect(mockOnSettings).toHaveBeenCalledTimes(1);
  });

  it('should show saving state', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={true}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByText('Sauvegarde...')).toBeInTheDocument();
    const saveButton = screen.getByRole('button', { name: /sauvegarde/i });
    expect(saveButton).toBeDisabled();
  });

  it('should show unsaved changes indicator', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={false}
        hasUnsavedChanges={true}
      />
    );

    // Should show a dot or indicator for unsaved changes
    expect(screen.getByText('•')).toBeInTheDocument();
  });

  it('should show keyboard shortcuts in tooltips', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={false}
        hasUnsavedChanges={false}
      />
    );

    expect(screen.getByTitle(/Cmd\+S/i)).toBeInTheDocument();
    expect(screen.getByTitle(/Cmd\+P/i)).toBeInTheDocument();
    expect(screen.getByTitle(/Cmd\+E/i)).toBeInTheDocument();
  });

  it('should disable buttons during save', () => {
    render(
      <Toolbar
        onSave={mockOnSave}
        onPreview={mockOnPreview}
        onExport={mockOnExport}
        onSettings={mockOnSettings}
        isSaving={true}
        hasUnsavedChanges={false}
      />
    );

    const saveButton = screen.getByRole('button', { name: /sauvegarde/i });
    expect(saveButton).toBeDisabled();
  });
});
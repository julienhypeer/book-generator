import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PreviewToolbar } from './PreviewToolbar';

describe('PreviewToolbar', () => {
  const mockOnRefresh = vi.fn();
  const mockOnExport = vi.fn();
  const mockOnZoomChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render all toolbar buttons', () => {
    render(
      <PreviewToolbar
        onRefresh={mockOnRefresh}
        onExport={mockOnExport}
        onZoomChange={mockOnZoomChange}
        zoom={100}
        isLoading={false}
      />
    );

    expect(screen.getByRole('button', { name: /actualiser/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /exporter/i })).toBeInTheDocument();
    expect(screen.getByDisplayValue('100%')).toBeInTheDocument();
  });

  it('should call onRefresh when refresh button is clicked', () => {
    render(
      <PreviewToolbar
        onRefresh={mockOnRefresh}
        onExport={mockOnExport}
        onZoomChange={mockOnZoomChange}
        zoom={100}
        isLoading={false}
      />
    );

    const refreshButton = screen.getByRole('button', { name: /actualiser/i });
    fireEvent.click(refreshButton);

    expect(mockOnRefresh).toHaveBeenCalledTimes(1);
  });

  it('should call onExport when export button is clicked', () => {
    render(
      <PreviewToolbar
        onRefresh={mockOnRefresh}
        onExport={mockOnExport}
        onZoomChange={mockOnZoomChange}
        zoom={100}
        isLoading={false}
      />
    );

    const exportButton = screen.getByRole('button', { name: /exporter/i });
    fireEvent.click(exportButton);

    expect(mockOnExport).toHaveBeenCalledTimes(1);
  });

  it('should call onZoomChange when zoom changes', () => {
    render(
      <PreviewToolbar
        onRefresh={mockOnRefresh}
        onExport={mockOnExport}
        onZoomChange={mockOnZoomChange}
        zoom={100}
        isLoading={false}
      />
    );

    const zoomSelect = screen.getByDisplayValue('100%');
    fireEvent.change(zoomSelect, { target: { value: '150' } });

    expect(mockOnZoomChange).toHaveBeenCalledWith(150);
  });

  it('should show loading state', () => {
    render(
      <PreviewToolbar
        onRefresh={mockOnRefresh}
        onExport={mockOnExport}
        onZoomChange={mockOnZoomChange}
        zoom={100}
        isLoading={true}
      />
    );

    const refreshButton = screen.getByRole('button', { name: /actualiser/i });
    expect(refreshButton).toBeDisabled();
  });

  it('should show correct zoom levels', () => {
    render(
      <PreviewToolbar
        onRefresh={mockOnRefresh}
        onExport={mockOnExport}
        onZoomChange={mockOnZoomChange}
        zoom={100}
        isLoading={false}
      />
    );

    const zoomSelect = screen.getByDisplayValue('100%');
    expect(zoomSelect).toBeInTheDocument();

    // Check that all zoom options are available
    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText('125%')).toBeInTheDocument();
    expect(screen.getByText('150%')).toBeInTheDocument();
    expect(screen.getByText('200%')).toBeInTheDocument();
  });

  it('should display current zoom level', () => {
    render(
      <PreviewToolbar
        onRefresh={mockOnRefresh}
        onExport={mockOnExport}
        onZoomChange={mockOnZoomChange}
        zoom={150}
        isLoading={false}
      />
    );

    expect(screen.getByDisplayValue('150%')).toBeInTheDocument();
  });
});
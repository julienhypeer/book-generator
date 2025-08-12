import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExportOptions } from './ExportOptions';

describe('ExportOptions', () => {
  const defaultOptions = {
    format: 'pdf' as const,
    template: 'roman' as const,
    include_toc: true,
    quality_validation: true,
  };

  const mockOnChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render format selection', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    expect(screen.getByText('Format d\'export')).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /PDF/i })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /EPUB/i })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /DOCX/i })).toBeInTheDocument();
  });

  it('should show selected format', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    const pdfRadio = screen.getByRole('radio', { name: /PDF/i });
    expect(pdfRadio).toBeChecked();
  });

  it('should call onChange when format changes', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    const epubRadio = screen.getByRole('radio', { name: /EPUB/i });
    fireEvent.click(epubRadio);

    expect(mockOnChange).toHaveBeenCalledWith({
      ...defaultOptions,
      format: 'epub',
    });
  });

  it('should show template options for PDF format', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    expect(screen.getByText('Template')).toBeInTheDocument();
    const templateSelect = screen.getByRole('combobox');
    expect(templateSelect).toBeInTheDocument();
    expect(templateSelect).toHaveValue('roman');
  });

  it('should hide template options for non-PDF formats', () => {
    const epubOptions = { ...defaultOptions, format: 'epub' as const };
    
    render(
      <ExportOptions 
        options={epubOptions} 
        onChange={mockOnChange} 
      />
    );

    expect(screen.queryByText('Template')).not.toBeInTheDocument();
  });

  it('should show quality validation option for PDF', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    expect(screen.getByText('Validation qualité')).toBeInTheDocument();
    const qualityCheckbox = screen.getByRole('checkbox', { name: /validation qualité/i });
    expect(qualityCheckbox).toBeChecked();
  });

  it('should show TOC option', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    expect(screen.getByText('Table des matières')).toBeInTheDocument();
    const tocCheckbox = screen.getByRole('checkbox', { name: /table des matières/i });
    expect(tocCheckbox).toBeChecked();
  });

  it('should call onChange when TOC option changes', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    const tocCheckbox = screen.getByRole('checkbox', { name: /table des matières/i });
    fireEvent.click(tocCheckbox);

    expect(mockOnChange).toHaveBeenCalledWith({
      ...defaultOptions,
      include_toc: false,
    });
  });

  it('should call onChange when template changes', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    const templateSelect = screen.getByRole('combobox');
    fireEvent.change(templateSelect, { target: { value: 'technical' } });

    expect(mockOnChange).toHaveBeenCalledWith({
      ...defaultOptions,
      template: 'technical',
    });
  });

  it('should show format descriptions', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    expect(screen.getByText(/Livre professionnel pour impression/)).toBeInTheDocument();
    expect(screen.getByText(/Livre électronique pour liseuses/)).toBeInTheDocument();
    expect(screen.getByText(/Document Word éditable/)).toBeInTheDocument();
  });

  it('should show template descriptions', () => {
    render(
      <ExportOptions 
        options={defaultOptions} 
        onChange={mockOnChange} 
      />
    );

    expect(screen.getByText(/Roman, fiction, littéraire/)).toBeInTheDocument();
  });
});
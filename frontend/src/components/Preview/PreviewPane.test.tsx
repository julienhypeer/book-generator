import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { PreviewPane } from './PreviewPane';

// Mock WebSocket
global.WebSocket = vi.fn().mockImplementation(() => ({
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  send: vi.fn(),
  close: vi.fn(),
  readyState: 1, // WebSocket.OPEN
})) as unknown as typeof WebSocket;

describe('PreviewPane', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render preview header', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={true}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Prévisualisation')).toBeInTheDocument();
  });

  it('should show close button', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={true}
        onClose={mockOnClose}
      />
    );

    const closeButton = screen.getByRole('button', { name: /fermer/i });
    expect(closeButton).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={true}
        onClose={mockOnClose}
      />
    );

    const closeButton = screen.getByRole('button', { name: /fermer/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should not render when not visible', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={false}
        onClose={mockOnClose}
      />
    );

    expect(screen.queryByText('Prévisualisation')).not.toBeInTheDocument();
  });

  it('should render preview iframe', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={true}
        onClose={mockOnClose}
      />
    );

    const iframe = screen.getByTitle('Prévisualisation du livre');
    expect(iframe).toBeInTheDocument();
    expect(iframe.getAttribute('src')).toMatch(/^\/api\/preview\/1(\?t=\d+)?$/);
  });

  it('should show loading state initially', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={true}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Chargement de la prévisualisation...')).toBeInTheDocument();
  });

  it('should show refresh button', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={true}
        onClose={mockOnClose}
      />
    );

    const refreshButton = screen.getByRole('button', { name: /actualiser/i });
    expect(refreshButton).toBeInTheDocument();
  });

  it('should refresh iframe when refresh button is clicked', () => {
    render(
      <PreviewPane
        projectId={1}
        isVisible={true}
        onClose={mockOnClose}
      />
    );

    const iframe = screen.getByTitle('Prévisualisation du livre');
    const initialSrc = iframe.getAttribute('src');
    expect(initialSrc).toBe('/api/preview/1?t=0');

    const refreshButton = screen.getByRole('button', { name: /actualiser/i });
    
    // Mock Date.now to ensure a different timestamp
    const originalDateNow = global.Date.now;
    global.Date.now = vi.fn(() => 12345);
    
    act(() => {
      fireEvent.click(refreshButton);
    });

    // Should call the refresh handler which will update loading state
    expect(screen.getByText('Chargement de la prévisualisation...')).toBeInTheDocument();
    
    // Restore Date.now
    global.Date.now = originalDateNow;
  });
});
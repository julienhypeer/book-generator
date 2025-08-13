import React, { useState, useEffect, useRef } from 'react';
import { PreviewToolbar } from './PreviewToolbar';

interface PreviewPaneProps {
  projectId: number;
  isVisible: boolean;
  onClose: () => void;
  onExport?: () => void;
}

export const PreviewPane: React.FC<PreviewPaneProps> = ({
  projectId,
  isVisible,
  onClose,
  onExport,
}) => {
  const [zoom, setZoom] = useState(100);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!isVisible || !projectId) return;

    // Use the same host as the frontend but on backend port
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname;
    const wsPort = 8000; // Backend port
    const ws = new WebSocket(`${wsProtocol}//${wsHost}:${wsPort}/ws/preview/${projectId}`);

    ws.onopen = () => {
      console.log('WebSocket connected for preview');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'content_updated') {
        // Refresh preview when content changes
        handleRefresh();
      }
    };

    return () => {
      ws.close();
    };
  }, [projectId, isVisible]);

  const handleRefresh = () => {
    setIsLoading(true);
    setRefreshKey(Date.now());
  };

  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  const handleZoomChange = (newZoom: number) => {
    setZoom(newZoom);
  };

  // Use the backend API URL for preview
  const apiUrl = `http://${window.location.hostname}:8000/api`;
  const previewUrl = `${apiUrl}/projects/${projectId}/preview?t=${refreshKey}`;

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-40 flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-100 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          Prévisualisation
        </h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          title="Fermer la prévisualisation"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Toolbar */}
      <PreviewToolbar
        onRefresh={handleRefresh}
        onExport={onExport || (() => {})}
        onZoomChange={handleZoomChange}
        zoom={zoom}
        isLoading={isLoading}
      />

      {/* Preview Content */}
      <div className="flex-1 relative bg-gray-200 overflow-auto">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
            <div className="text-center">
              <svg className="animate-spin mx-auto h-8 w-8 text-blue-600 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-sm text-gray-600">Chargement de la prévisualisation...</p>
            </div>
          </div>
        )}

        <div 
          className="flex justify-center p-4"
          style={{ minHeight: '100%' }}
        >
          <div 
            className="bg-white shadow-lg"
            style={{ 
              transform: `scale(${zoom / 100})`,
              transformOrigin: 'top center',
              transition: 'transform 0.2s ease-in-out'
            }}
          >
            <iframe
              ref={iframeRef}
              src={previewUrl}
              title="Prévisualisation du livre"
              className="w-full border-none"
              style={{
                width: '794px', // A4 width in pixels at 96 DPI
                height: '1123px', // A4 height in pixels at 96 DPI
              }}
              onLoad={handleIframeLoad}
              onError={() => setIsLoading(false)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
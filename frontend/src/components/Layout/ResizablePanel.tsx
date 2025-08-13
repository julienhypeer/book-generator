import React, { useState, useEffect, useRef } from 'react';

interface ResizablePanelProps {
  children: React.ReactNode;
  defaultWidth?: number;
  minWidth?: number;
  maxWidth?: number;
  storageKey?: string;
  className?: string;
}

export const ResizablePanel: React.FC<ResizablePanelProps> = ({
  children,
  defaultWidth = 300,
  minWidth = 200,
  maxWidth = 500,
  storageKey = 'sidebar-width',
  className = '',
}) => {
  const [width, setWidth] = useState(() => {
    // Récupérer la largeur sauvegardée dans localStorage
    const savedWidth = localStorage.getItem(storageKey);
    return savedWidth ? parseInt(savedWidth, 10) : defaultWidth;
  });
  
  const [isResizing, setIsResizing] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Sauvegarder la largeur dans localStorage
    localStorage.setItem(storageKey, width.toString());
  }, [width, storageKey]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      const newWidth = e.clientX;
      
      // Limiter la largeur entre min et max
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };

    if (isResizing) {
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, minWidth, maxWidth]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  };

  return (
    <div 
      ref={panelRef}
      className={`relative flex-shrink-0 ${className}`}
      style={{ width: `${width}px` }}
    >
      {/* Contenu du panel */}
      {children}
      
      {/* Poignée de redimensionnement */}
      <div
        className={`absolute top-0 right-0 h-full w-1 cursor-col-resize hover:bg-blue-400 transition-colors ${
          isResizing ? 'bg-blue-500' : 'bg-gray-300'
        }`}
        onMouseDown={handleMouseDown}
        style={{ width: '4px', right: '-2px' }}
      >
        {/* Indicateur visuel au centre de la poignée */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="flex flex-col gap-1">
            <div className="w-1 h-1 bg-gray-400 rounded-full" />
            <div className="w-1 h-1 bg-gray-400 rounded-full" />
            <div className="w-1 h-1 bg-gray-400 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
};
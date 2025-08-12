import { useEffect, useCallback } from 'react';
import { useEditorStore } from '@/stores/editorStore';

export const useMemoryCleanup = () => {
  const { cleanup, getMemoryUsage } = useEditorStore();
  
  // Manual cleanup function
  const cleanupNow = useCallback(() => {
    cleanup();
  }, [cleanup]);
  
  // Get current memory usage
  const getUsage = useCallback(() => {
    return getMemoryUsage();
  }, [getMemoryUsage]);
  
  // Automatic cleanup on unmount or when memory usage is high
  useEffect(() => {
    const checkAndCleanup = () => {
      const usage = getMemoryUsage();
      
      // Clean up if total size exceeds 50MB or too many chapters
      if (usage.totalSize > 50 * 1024 || usage.chapters > 100) {
        cleanup();
      }
    };
    
    // Check memory usage every 5 minutes
    const interval = setInterval(checkAndCleanup, 5 * 60 * 1000);
    
    // Cleanup on component unmount
    return () => {
      clearInterval(interval);
      cleanup();
    };
  }, [cleanup, getMemoryUsage]);
  
  // Listen for page visibility change to cleanup when hidden
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is now hidden, do cleanup
        cleanup();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [cleanup]);
  
  return {
    cleanupNow,
    getUsage,
  };
};
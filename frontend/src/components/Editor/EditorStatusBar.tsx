import React from 'react';
import { useEditorStore } from '@/stores/editorStore';
import { useAutoSave } from '@/hooks/useAutoSave';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline';

export const EditorStatusBar: React.FC = () => {
  const { 
    chapters, 
    activeChapterId, 
    content, 
    settings,
    unsavedChanges 
  } = useEditorStore();
  
  const { isSaving, hasUnsavedChanges } = useAutoSave();

  const activeChapter = chapters.find(c => c.id === activeChapterId);
  const chapterContent = activeChapterId ? content.get(activeChapterId) || '' : '';
  
  // Calculate word count
  const wordCount = chapterContent
    .trim()
    .split(/\s+/)
    .filter(word => word.length > 0).length;
  
  // Calculate character count
  const charCount = chapterContent.length;
  
  // Calculate line count
  const lineCount = chapterContent.split('\n').length;

  // Save status
  const getSaveStatus = () => {
    if (isSaving) {
      return {
        icon: <ArrowPathIcon className="h-4 w-4 animate-spin" />,
        text: 'Saving...',
        className: 'text-blue-600',
      };
    }
    
    if (hasUnsavedChanges) {
      return {
        icon: <ExclamationCircleIcon className="h-4 w-4" />,
        text: 'Unsaved changes',
        className: 'text-orange-600',
      };
    }
    
    return {
      icon: <CheckCircleIcon className="h-4 w-4" />,
      text: 'All changes saved',
      className: 'text-green-600',
    };
  };

  const saveStatus = getSaveStatus();

  return (
    <div className="flex items-center justify-between border-t border-gray-200 bg-gray-50 px-4 py-1 text-xs">
      {/* Left section - Chapter info */}
      <div className="flex items-center gap-4">
        {activeChapter && (
          <>
            <span className="text-gray-600">
              Chapter {activeChapter.position}: {activeChapter.title}
            </span>
            <span className="text-gray-400">|</span>
          </>
        )}
        
        {/* Statistics */}
        <div className="flex items-center gap-3 text-gray-600">
          <span>Lines: {lineCount.toLocaleString()}</span>
          <span>Words: {wordCount.toLocaleString()}</span>
          <span>Characters: {charCount.toLocaleString()}</span>
        </div>
      </div>

      {/* Center section - Save status */}
      <div className={`flex items-center gap-1 ${saveStatus.className}`}>
        {saveStatus.icon}
        <span>{saveStatus.text}</span>
      </div>

      {/* Right section - Settings info */}
      <div className="flex items-center gap-4 text-gray-600">
        {/* Auto-save status */}
        {settings.autoSave ? (
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-green-400" />
            Auto-save: {settings.autoSaveDelay / 1000}s
          </span>
        ) : (
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-gray-400" />
            Auto-save: Off
          </span>
        )}
        
        <span className="text-gray-400">|</span>
        
        {/* Editor settings */}
        <span>Font: {settings.fontSize}px</span>
        <span>Theme: {settings.theme === 'vs-dark' ? 'Dark' : 'Light'}</span>
        
        {/* Unsaved chapters count */}
        {unsavedChanges.size > 1 && (
          <>
            <span className="text-gray-400">|</span>
            <span className="text-orange-600">
              {unsavedChanges.size} unsaved chapters
            </span>
          </>
        )}
      </div>
    </div>
  );
};
// Type definitions for the book generator

export interface Project {
  id: number;
  title: string;
  author: string;
  description?: string;
  settings?: ProjectSettings;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: number;
  project_id: number;
  title: string;
  content: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectSettings {
  template?: 'roman' | 'technical' | 'academic';
  page_format?: 'A4' | 'A5' | 'Letter';
  font_family?: string;
  font_size?: number;
  line_height?: number;
  margins?: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  page_numbers?: boolean;
  table_of_contents?: boolean;
  hyphenation?: boolean;
}

export interface EditorSettings {
  fontSize: number;
  lineHeight: number;
  wordWrap: 'on' | 'off' | 'wordWrapColumn' | 'bounded';
  minimap: boolean;
  theme: 'vs' | 'vs-dark' | 'hc-black' | 'hc-light' | 'vs-light';
  autoSave: boolean;
  autoSaveDelay: number;
}

export interface ExportOptions {
  format: 'pdf' | 'html' | 'markdown' | 'docx' | 'epub';
  template: 'roman' | 'technical' | 'academic';
  includeTableOfContents: boolean;
  includePageNumbers: boolean;
  paperSize: 'a4' | 'letter' | 'book';
}

// Extend global Window interface for memory management
declare global {
  interface Window {
    gc?: () => void;
  }
}
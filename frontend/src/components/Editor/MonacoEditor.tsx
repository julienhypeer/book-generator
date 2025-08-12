import React, { useCallback, useRef } from 'react';
import Editor, { OnMount, OnChange, BeforeMount } from '@monaco-editor/react';
import { editor } from 'monaco-editor';
import { useEditorStore } from '@/stores/editorStore';
import { useAutoSave } from '@/hooks/useAutoSave';

interface MonacoEditorProps {
  chapterId: number;
  content: string;
  onChange?: (content: string) => void;
}

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  chapterId,
  content,
  onChange,
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const { settings, updateChapterContent } = useEditorStore();
  
  // Auto-save hook
  useAutoSave();

  // Configure Monaco before mount
  const handleEditorWillMount: BeforeMount = (monaco) => {
    // Configure Markdown language features
    monaco.languages.setLanguageConfiguration('markdown', {
      wordPattern: /(-?\d*\.\d\w*)|([^`~!@#%^&*()-=+[{}\\|;:'",./<>?\s]+)/g,
      comments: {
        blockComment: ['<!--', '-->']
      },
      brackets: [
        ['{', '}'],
        ['[', ']'],
        ['(', ')']
      ],
      autoClosingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
        { open: '`', close: '`' },
        { open: '*', close: '*' },
        { open: '_', close: '_' },
        { open: '**', close: '**' },
        { open: '__', close: '__' },
        { open: '<!--', close: '-->' }
      ],
      surroundingPairs: [
        { open: '(', close: ')' },
        { open: '[', close: ']' },
        { open: '`', close: '`' },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
        { open: '*', close: '*' },
        { open: '_', close: '_' },
        { open: '**', close: '**' },
        { open: '__', close: '__' }
      ],
      folding: {
        markers: {
          start: new RegExp("^\\s*<!--\\s*#region\\b.*-->"),
          end: new RegExp("^\\s*<!--\\s*#endregion\\b.*-->")
        }
      }
    });

    // Register Markdown snippets
    monaco.languages.registerCompletionItemProvider('markdown', {
      provideCompletionItems: (_model, _position) => {
        const suggestions = [
          {
            label: 'h1',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '# ${1:heading}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Heading level 1'
          },
          {
            label: 'h2',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '## ${1:heading}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Heading level 2'
          },
          {
            label: 'h3',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '### ${1:heading}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Heading level 3'
          },
          {
            label: 'link',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '[${1:text}](${2:url})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Link'
          },
          {
            label: 'image',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '![${1:alt text}](${2:url})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Image'
          },
          {
            label: 'bold',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '**${1:text}**',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Bold text'
          },
          {
            label: 'italic',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '*${1:text}*',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Italic text'
          },
          {
            label: 'code',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '`${1:code}`',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Inline code'
          },
          {
            label: 'codeblock',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '```${1:language}\n${2:code}\n```',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Code block'
          },
          {
            label: 'ul',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '- ${1:item}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Unordered list item'
          },
          {
            label: 'ol',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '1. ${1:item}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Ordered list item'
          },
          {
            label: 'blockquote',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '> ${1:quote}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Blockquote'
          },
          {
            label: 'hr',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '---',
            documentation: 'Horizontal rule'
          },
          {
            label: 'table',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '| ${1:Column 1} | ${2:Column 2} |\n| --- | --- |\n| ${3:Cell 1} | ${4:Cell 2} |',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Table'
          }
        ];
        
        return { suggestions };
      }
    });
  };

  const handleEditorDidMount: OnMount = (editor) => {
    editorRef.current = editor;
    
    // Configure editor
    editor.updateOptions({
      fontSize: settings.fontSize,
      lineHeight: settings.lineHeight * settings.fontSize,
      wordWrap: settings.wordWrap,
      minimap: { enabled: settings.minimap },
      scrollBeyondLastLine: false,
      renderWhitespace: 'selection',
      formatOnPaste: true,
      formatOnType: true,
    });

    // Add custom actions
    editor.addAction({
      id: 'save-chapter',
      label: 'Save Chapter',
      keybindings: [
        // Cmd+S on Mac, Ctrl+S on Windows/Linux
        editor.KeyMod.CtrlCmd | editor.KeyCode.KeyS,
      ],
      run: () => {
        // Trigger save action
        const content = editor.getValue();
        updateChapterContent(chapterId, content);
      },
    });

    // Focus editor
    editor.focus();
  };

  const handleEditorChange: OnChange = useCallback(
    (value) => {
      if (value !== undefined) {
        updateChapterContent(chapterId, value);
        onChange?.(value);
      }
    },
    [chapterId, updateChapterContent, onChange]
  );

  return (
    <div className="h-full w-full">
      <Editor
        defaultLanguage="markdown"
        language="markdown"
        value={content}
        theme={settings.theme}
        beforeMount={handleEditorWillMount}
        onMount={handleEditorDidMount}
        onChange={handleEditorChange}
        options={{
          automaticLayout: true,
          fontSize: settings.fontSize,
          lineHeight: settings.lineHeight * settings.fontSize,
          wordWrap: settings.wordWrap,
          minimap: { enabled: settings.minimap },
          scrollBeyondLastLine: false,
          renderWhitespace: 'selection',
          formatOnPaste: true,
          formatOnType: true,
          // Markdown-specific options
          quickSuggestions: {
            other: true,
            comments: true,
            strings: true,
          },
          acceptSuggestionOnCommitCharacter: true,
          snippetSuggestions: 'inline',
          tabSize: 2,
          insertSpaces: true,
          trimAutoWhitespace: true,
          // Accessibility
          accessibilitySupport: 'auto',
          screenReaderAnnounceInlineSuggestion: true,
        }}
      />
    </div>
  );
};
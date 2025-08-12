# 🎨 Frontend - Instructions Claude

## 📋 Contexte
Interface React pour l'édition et la génération de livres professionnels.

## 🏗️ Architecture

### Structure des Composants
```
/components
  /Editor         → Éditeur Monaco + gestion chapitres
  /Layout         → Templates et mise en page
  /Export         → Options d'export et preview PDF
  /Preview        → Prévisualisation temps réel
```

### State Management (Zustand)
```typescript
// stores/editorStore.ts
interface EditorState {
  chapters: Chapter[]
  activeChapter: string
  content: Map<string, string>
  settings: BookSettings
}
```

### Hooks Principaux
- `useAutoSave()` : Sauvegarde automatique toutes les 30s
- `useWebSocket()` : Preview temps réel via WebSocket
- `useShortcuts()` : Raccourcis clavier (Cmd+S, Cmd+P, etc.)
- `useChapterNavigation()` : Navigation entre chapitres

## 🎯 Fonctionnalités Critiques

### 1. Éditeur Monaco
```typescript
// Configuration spéciale pour Markdown
const editorOptions = {
  language: 'markdown',
  wordWrap: 'on',
  minimap: { enabled: false },
  fontSize: 16,
  lineHeight: 24,
  formatOnPaste: true,
}
```

### 2. Preview Temps Réel
- WebSocket pour mise à jour instantanée
- Debounce de 500ms pour éviter surcharge
- Cache côté client avec TanStack Query

### 3. Gestion Chapitres
- Drag & drop pour réorganiser
- Numérotation automatique
- Métadonnées par chapitre (titre, sous-titre, page de garde)

## 🐛 Problèmes Connus et Solutions

### Monaco Editor Bundle Size
```typescript
// Lazy loading obligatoire
const MonacoEditor = lazy(() => import('@monaco-editor/react'))
```

### WebSocket Reconnection
```typescript
// Auto-reconnect avec exponential backoff
const reconnect = useCallback(() => {
  setTimeout(() => connect(), Math.min(1000 * Math.pow(2, attempts), 30000))
}, [attempts])
```

## 🎨 Styles et Thèmes

### CSS Print Media
```css
@media print {
  .no-print { display: none; }
  .page-break { page-break-after: always; }
}
```

### Dark Mode
Utiliser CSS variables pour switcher facilement :
```css
:root {
  --bg-primary: white;
  --text-primary: black;
}
[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: white;
}
```

## 🔧 Commandes

```bash
# Développement
npm run dev

# Build production
npm run build

# Tests
npm test
npm run test:coverage

# Linting
npm run lint
npm run format
```

## 📊 Métriques de Performance

- Bundle size < 500KB (initial)
- First paint < 1.5s
- TTI < 3s
- Preview update < 500ms

## 🚀 Optimisations

1. **Code Splitting** : Monaco chargé à la demande
2. **Virtual Scrolling** : Pour longs chapitres
3. **Web Workers** : Parsing Markdown en background
4. **Service Worker** : Cache offline des projets

## ✅ État du Développement

### PR #8 - Frontend Corrections (Complété)
- ✅ Fix des tests Vitest dans useAutoSave.test.tsx (2 tests échouant)
- ✅ Ajout de 4 méthodes de gestion mémoire à editorStore
  - `clearUnusedContent()` - Nettoie le contenu des chapitres supprimés
  - `forceCleanup()` - Nettoyage forcé avec garbage collection
  - `getMemoryUsage()` - Monitore l'utilisation mémoire
  - `resetToDefaults()` - Réinitialise l'état par défaut
- ✅ Création hook useMemoryCleanup avec monitoring automatique
- ✅ Extension interface Window pour garbage collection
- ✅ Tests passent maintenant correctement avec async/await
- ✅ Code formaté et linté

### Corrections Techniques
```typescript
// Avant: Tests timeout à 5000ms avec mutations
expect(saveMutation.mutateAsync).toHaveBeenCalledWith({
  chapterId: 1, projectId: 1, data: { content: 'Updated Content' }
});

// Après: Tests basés sur comportement hook
expect(result.current.hasUnsavedChanges).toBe(true);
act(() => { vi.advanceTimersByTime(100); });
expect(chapterService.updateChapter).toHaveBeenCalledWith(1, 1, { content: 'Updated Content' });
```

### Memory Management
```typescript
// Cleanup automatique toutes les 5 minutes
const useMemoryCleanup = () => {
  const { cleanup, getMemoryUsage } = useEditorStore();
  
  useEffect(() => {
    const checkAndCleanup = () => {
      const usage = getMemoryUsage();
      if (usage.totalSize > 50 * 1024 || usage.chapters > 100) {
        cleanup();
      }
    };
    const interval = setInterval(checkAndCleanup, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [cleanup, getMemoryUsage]);
};
```

### Structure Actuelle
```
/src
  /components   → Composants React (Editor, Layout, Export)
  /stores       → State Zustand avec persistence et cleanup ✅
  /hooks        → Hooks (useAutoSave ✅, useMemoryCleanup ✅)
  /services     → Services API (TanStack Query)
  /utils        → Utilitaires et helpers
  /types        → Types TypeScript partagés
```
import { useEffect } from 'react';
import { KEY_MAP } from './keymap';
import { useCommandRegistry } from '../commands/commands.registry';

const normalizeKey = (e: KeyboardEvent): string => {
  let key = e.key.toLowerCase();
  
  if (e.metaKey || e.ctrlKey) {
    if (key === 'k') return 'k';
    if (key === 't') return 't';
    if (key === 'n') return 'n';
    if (key >= '1' && key <= '9') return key;
    if (key === 'i') return 'i';
  }

  if (key === 'enter') return 'enter';
  if (key === 'escape') return 'escape';
  if (key === '/') return '/';

  return '';
};

const getNormalizedShortcut = (e: KeyboardEvent): string => {
  const normalizedKey = normalizeKey(e);
  if (!normalizedKey) return '';

  const isModifier = e.metaKey || e.ctrlKey;
  
  if (isModifier) {
    // Treat Ctrl and Cmd (Meta) as interchangeable for application shortcuts
    return normalizedKey;
  }
  
  return normalizedKey;
};

export function useShortcutListener() {
  const { executeCommand } = useCommandRegistry();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const normalizedShortcut = getNormalizedShortcut(e);

      if (!normalizedShortcut) {
        return;
      }

      // Find the matching global shortcut
      const shortcut = KEY_MAP.find(
        (map) => 
          map.global && 
          map.key === normalizedShortcut && 
          (
            // Check for modifier keys for non-special keys
            map.display.includes('⌘') && (e.metaKey || e.ctrlKey)
            // Check for non-modifier keys (e.g., '/', 'Escape')
            || (!map.display.includes('⌘') && !e.metaKey && !e.ctrlKey)
          )
      );

      if (shortcut) {
        // Prevent default browser actions for common shortcuts (e.g., Cmd+K, Cmd+T)
        e.preventDefault();
        e.stopPropagation();
        executeCommand(shortcut.commandId);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [executeCommand]);
}
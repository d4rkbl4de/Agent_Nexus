import React, { createContext, useContext, useState, useMemo, useCallback, useEffect } from 'react';

export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeState {
  mode: ThemeMode;
  resolvedMode: 'light' | 'dark';
}

export interface ThemeContextType extends ThemeState {
  setMode: (mode: ThemeMode) => void;
}

const STORAGE_KEY = 'agentNexusTheme';
const DEFAULT_MODE: ThemeMode = 'system';

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const getStoredMode = (): ThemeMode => {
  const stored = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
  return stored || DEFAULT_MODE;
};

const resolveThemeMode = (mode: ThemeMode): 'light' | 'dark' => {
  if (mode === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return mode;
};

const applyThemeToDOM = (resolvedMode: 'light' | 'dark'): void => {
  const root = document.documentElement;
  root.classList.remove('light', 'dark');
  root.classList.add(resolvedMode);
  root.style.colorScheme = resolvedMode;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [mode, setModeState] = useState<ThemeMode>(getStoredMode);
  
  const resolvedMode = useMemo(() => resolveThemeMode(mode), [mode]);

  const setMode = useCallback((newMode: ThemeMode) => {
    setModeState(newMode);
    localStorage.setItem(STORAGE_KEY, newMode);
  }, []);

  useEffect(() => {
    applyThemeToDOM(resolvedMode);
  }, [resolvedMode]);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = () => {
      if (mode === 'system') {
        const newResolvedMode = resolveThemeMode(mode);
        applyThemeToDOM(newResolvedMode);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [mode]);

  const value = useMemo(() => ({
    mode,
    resolvedMode,
    setMode,
  }), [mode, resolvedMode, setMode]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
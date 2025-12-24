import { darkTheme } from './dark'
import { lightTheme } from './light'

export type ThemeMode = 'light' | 'dark' | 'system'

export const resolveSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export const getTheme = (mode: ThemeMode) => {
  if (mode === 'system') {
    const resolved = resolveSystemTheme()
    return resolved === 'dark' ? darkTheme : lightTheme
  }
  return mode === 'dark' ? darkTheme : lightTheme
}

export const systemTheme = {
  id: 'system',
  mode: 'system',
  resolve: getTheme
} as const

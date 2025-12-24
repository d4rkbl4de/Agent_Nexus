import { colors } from '../tokens/colors'
import { radii } from '../tokens/radii'
import { spacing } from '../tokens/spacing'
import { typography } from '../tokens/typography'

export const lightTheme = {
  id: 'light',
  mode: 'light',
  tokens: {
    colors: {
      background: colors.gray[50],
      surface: '#ffffff',
      surfaceAlt: colors.gray[100],
      foreground: colors.gray[900],
      muted: colors.gray[500],
      border: colors.gray[200],
      primary: colors.blue[600],
      primaryHover: colors.blue[700],
      success: colors.green[600],
      warning: colors.yellow[600],
      danger: colors.red[600]
    },
    radii,
    spacing,
    typography
  }
} as const

export type LightTheme = typeof lightTheme

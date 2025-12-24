import { colors } from '../tokens/colors'
import { radii } from '../tokens/radii'
import { spacing } from '../tokens/spacing'
import { typography } from '../tokens/typography'

export const darkTheme = {
  id: 'dark',
  mode: 'dark',
  tokens: {
    colors: {
      background: colors.gray[900],
      surface: colors.gray[800],
      surfaceAlt: colors.gray[700],
      foreground: colors.gray[50],
      muted: colors.gray[400],
      border: colors.gray[700],
      primary: colors.blue[500],
      primaryHover: colors.blue[400],
      success: colors.green[500],
      warning: colors.yellow[500],
      danger: colors.red[500]
    },
    radii,
    spacing,
    typography
  }
} as const

export type DarkTheme = typeof darkTheme

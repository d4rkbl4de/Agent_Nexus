export type Shortcut = {
  keys: string[]
  commandId: string
}

export const shortcuts: Shortcut[] = [
  { keys: ['Meta', 'K'], commandId: 'command-palette' },
  { keys: ['Control', 'K'], commandId: 'command-palette' }
]

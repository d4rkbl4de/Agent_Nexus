export type NotificationSound = 'success' | 'error' | 'warning' | 'info'

const sounds: Record<NotificationSound, string> = {
  success: '/sounds/success.mp3',
  error: '/sounds/error.mp3',
  warning: '/sounds/warning.mp3',
  info: '/sounds/info.mp3'
}

export const playSound = (type: NotificationSound) => {
  if (typeof window === 'undefined') return
  const src = sounds[type]
  if (!src) return
  const audio = new Audio(src)
  audio.volume = 0.6
  audio.play().catch(() => {})
}

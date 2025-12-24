'use client'

import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import Toast, { ToastType } from './Toast'
import { nanoid } from 'nanoid'

type Notification = {
  id: string
  title: string
  description?: string
  type: ToastType
  duration: number
}

type NotifyFn = (n: Omit<Notification, 'id'>) => void

const NotificationContext = createContext<NotifyFn | null>(null)

export function useNotify() {
  const ctx = useContext(NotificationContext)
  if (!ctx) {
    throw new Error('useNotify must be used within NotificationCenter')
  }
  return ctx
}

export default function NotificationCenter({
  children
}: {
  children: React.ReactNode
}) {
  const [items, setItems] = useState<Notification[]>([])

  const dismiss = useCallback((id: string) => {
    setItems(i => i.filter(n => n.id !== id))
  }, [])

  const notify = useCallback<NotifyFn>(
    n => {
      setItems(i => [
        ...i,
        {
          id: nanoid(),
          duration: 4000,
          ...n
        }
      ])
    },
    []
  )

  const value = useMemo(() => notify, [notify])

  return (
    <NotificationContext.Provider value={value}>
      {children}
      {typeof document !== 'undefined' &&
        createPortal(
          <div className="fixed right-4 top-4 z-50 flex flex-col gap-2">
            {items.map(t => (
              <Toast
                key={t.id}
                {...t}
                onDismiss={dismiss}
              />
            ))}
          </div>,
          document.body
        )}
    </NotificationContext.Provider>
  )
}

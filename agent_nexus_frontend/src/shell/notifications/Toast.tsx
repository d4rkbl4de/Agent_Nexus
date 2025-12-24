'use client'

import { useEffect } from 'react'
import clsx from 'clsx'
import { Icon } from '@/design-system/icons/Icon'
import { playSound, NotificationSound } from './sounds'

export type ToastType = NotificationSound

export type ToastProps = {
  id: string
  title: string
  description?: string
  type: ToastType
  duration: number
  onDismiss: (id: string) => void
}

const typeMap: Record<
  ToastType,
  { icon: any; className: string }
> = {
  success: { icon: 'success', className: 'border-green-500' },
  error: { icon: 'error', className: 'border-red-500' },
  warning: { icon: 'warning', className: 'border-yellow-500' },
  info: { icon: 'info', className: 'border-blue-500' }
}

export default function Toast({
  id,
  title,
  description,
  type,
  duration,
  onDismiss
}: ToastProps) {
  useEffect(() => {
    playSound(type)
    const t = setTimeout(() => onDismiss(id), duration)
    return () => clearTimeout(t)
  }, [id, duration, type, onDismiss])

  const meta = typeMap[type]

  return (
    <div
      className={clsx(
        'pointer-events-auto w-full max-w-sm rounded-lg border bg-background p-4 shadow-lg',
        meta.className
      )}
    >
      <div className="flex items-start gap-3">
        <Icon name={meta.icon} size={18} />
        <div className="flex-1">
          <div className="text-sm font-medium">{title}</div>
          {description && (
            <div className="mt-1 text-xs text-muted-foreground">
              {description}
            </div>
          )}
        </div>
        <button
          onClick={() => onDismiss(id)}
          className="text-muted-foreground hover:text-foreground"
        >
          ×
        </button>
      </div>
    </div>
  )
}

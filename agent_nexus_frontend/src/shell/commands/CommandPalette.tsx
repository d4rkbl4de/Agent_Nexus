'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { useRouter } from 'next/navigation'
import { commandRegistry, Command } from './commands.registry'
import { Icon } from '@/design-system/icons/Icon'
import { useSession } from '@/core/hooks/useSession'
import clsx from 'clsx'

export default function CommandPalette() {
  const router = useRouter()
  const { logout } = useSession()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [mounted, setMounted] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)

  const commands = useMemo(
    () =>
      commandRegistry().filter(c =>
        c.label.toLowerCase().includes(query.toLowerCase())
      ),
    [query]
  )

  const ctx = useMemo(
    () => ({
      push: router.push,
      logout
    }),
    [router.push, logout]
  )

  const execute = useCallback(
    async (command: Command) => {
      setOpen(false)
      setQuery('')
      setActiveIndex(0)
      await command.run(ctx)
    },
    [ctx]
  )

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!open) return

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
      if (e.key === 'ArrowDown')
        setActiveIndex(i => Math.min(i + 1, commands.length - 1))
      if (e.key === 'ArrowUp')
        setActiveIndex(i => Math.max(i - 1, 0))
      if (e.key === 'Enter' && commands[activeIndex])
        execute(commands[activeIndex])
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, commands, activeIndex, execute])

  useEffect(() => {
    const onGlobal = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setOpen(o => !o)
      }
    }

    window.addEventListener('keydown', onGlobal)
    return () => window.removeEventListener('keydown', onGlobal)
  }, [])

  if (!mounted) return null

  return createPortal(
    <div
      className={clsx(
        'fixed inset-0 z-50 flex items-start justify-center bg-black/40 transition',
        open ? 'opacity-100' : 'pointer-events-none opacity-0'
      )}
    >
      <div className="mt-24 w-full max-w-xl overflow-hidden rounded-lg border bg-background shadow-xl">
        <input
          autoFocus
          value={query}
          onChange={e => {
            setQuery(e.target.value)
            setActiveIndex(0)
          }}
          placeholder="Type a command..."
          className="w-full border-b bg-transparent px-4 py-3 text-sm outline-none"
        />
        <div className="max-h-96 overflow-y-auto">
          {commands.length === 0 && (
            <div className="px-4 py-6 text-center text-sm text-muted-foreground">
              No commands found
            </div>
          )}
          {commands.map((command, i) => (
            <button
              key={command.id}
              onClick={() => execute(command)}
              className={clsx(
                'flex w-full items-center gap-3 px-4 py-2 text-sm',
                i === activeIndex
                  ? 'bg-muted'
                  : 'hover:bg-muted/60'
              )}
            >
              <Icon name={command.icon} size={16} />
              <span className="flex-1 truncate">{command.label}</span>
              {command.shortcut && (
                <span className="flex gap-1 text-xs text-muted-foreground">
                  {command.shortcut.map(k => (
                    <kbd
                      key={k}
                      className="rounded border px-1.5 py-0.5"
                    >
                      {k}
                    </kbd>
                  ))}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>,
    document.body
  )
}

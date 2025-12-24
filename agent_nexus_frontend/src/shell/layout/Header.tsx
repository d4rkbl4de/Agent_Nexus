'use client'

import { useSession } from '@/core/hooks/useSession'
import { useSystem } from '@/core/hooks/useSystem'
import CommandPalette from '@/shell/commands/CommandPalette'
import NotificationCenter from '@/shell/notifications/NotificationCenter'

export default function Header() {
  const { session } = useSession()
  const { systemStatus } = useSystem()

  if (!session) return null

  return (
    <header className="flex h-14 items-center justify-between border-b bg-background px-4">
      <div className="flex items-center gap-3 text-sm font-medium">
        <span>{session.user.name}</span>
        <span className="text-xs text-muted-foreground">
          {systemStatus}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <CommandPalette />
        <NotificationCenter />
      </div>
    </header>
  )
}

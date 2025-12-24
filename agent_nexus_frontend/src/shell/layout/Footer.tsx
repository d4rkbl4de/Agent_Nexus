'use client'

import { useSystem } from '@/core/hooks/useSystem'

export default function Footer() {
  const { version, uptime } = useSystem()

  return (
    <footer className="flex h-10 items-center justify-between border-t bg-muted/20 px-4 text-xs text-muted-foreground">
      <span>Agent Nexus v{version}</span>
      <span>Uptime {uptime}</span>
    </footer>
  )
}

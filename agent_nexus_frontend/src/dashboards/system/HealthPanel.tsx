'use client'

import { useEffect, useState } from 'react'
import { Panel } from '@/design-system/layouts/Panel'
import { Stack } from '@/design-system/layouts/Stack'
import { useSystem } from '@/core/hooks/useSystem'

export default function HealthPanel() {
  const { health, refreshHealth } = useSystem()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    refreshHealth().finally(() => setReady(true))
  }, [refreshHealth])

  if (!ready || !health) {
    return <div className="h-full w-full animate-pulse bg-muted" />
  }

  return (
    <Panel>
      <Stack gap="md">
        <div className="text-sm font-semibold">System Health</div>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(health.services).map(([name, status]) => (
            <div
              key={name}
              className={`rounded-md border p-3 ${
                status === 'healthy'
                  ? 'border-green-500 text-green-500'
                  : 'border-red-500 text-red-500'
              }`}
            >
              <div className="text-xs uppercase">{name}</div>
              <div className="text-sm">{status}</div>
            </div>
          ))}
        </div>
        <div className="text-xs text-muted-foreground">
          Last checked {new Date(health.timestamp).toLocaleTimeString()}
        </div>
      </Stack>
    </Panel>
  )
}

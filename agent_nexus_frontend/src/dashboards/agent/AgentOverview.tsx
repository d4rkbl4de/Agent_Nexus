'use client'

import { useEffect, useState } from 'react'
import { useAgent } from '@/core/hooks/useAgent'
import { Panel } from '@/design-system/layouts/Panel'
import { Stack } from '@/design-system/layouts/Stack'

export default function AgentOverview() {
  const { agent, refresh } = useAgent()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    refresh().finally(() => setReady(true))
  }, [refresh])

  if (!ready || !agent) {
    return <div className="h-full w-full animate-pulse bg-muted" />
  }

  return (
    <Panel>
      <Stack gap="md">
        <div className="text-xl font-semibold">{agent.name}</div>
        <div className="text-sm text-muted-foreground">{agent.description}</div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs uppercase text-muted-foreground">Status</div>
            <div className="text-sm">{agent.status}</div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Mode</div>
            <div className="text-sm">{agent.mode}</div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Last Active</div>
            <div className="text-sm">
              {new Date(agent.lastActive).toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase text-muted-foreground">Tasks</div>
            <div className="text-sm">{agent.taskCount}</div>
          </div>
        </div>
      </Stack>
    </Panel>
  )
}
